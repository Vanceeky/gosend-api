from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.admin_schemas import AdminAccountCreate, AdminLoginRequest
from utils.responses import json_response


from fastapi import HTTPException
from api.v1.repo.admin_repo import AdminRepo
from core.security import verify_password, sign_jwt

from api.v1.services.TopWallet import TopWallet
from models.activation_history_models import ActivationHistory
from models.reward_models import Reward
from models.wallet_models import Wallet
from models.member_models import MemberWallet
from sqlalchemy.future import select



from api.v1.repo.member_repo import MemberRepo


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # or configure a FileHandler as needed
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



class AdminService:
    @staticmethod
    async def create_account(db: AsyncSession, admin_data: AdminAccountCreate):
        
        result = await AdminRepo.create_account(db, admin_data)

        if result["status_code"] == 200:
            logger.info("Account created successfully: %s", result["data"]["id"])
        elif result["status_code"] == 400:
            logger.warning("Failed to create account: %s", result["message"])
        else:
            logger.error("Unexpected error during account creation")

        return json_response(
            status_code=result['status_code'],
            message = result['message'],
            data = result['data'] 
        )
    

    @staticmethod
    async def login_account(db: AsyncSession, account_url: str, login_data: AdminLoginRequest):
        from api.v1.repo.member_repo import MemberRepo
        try:
            account = await AdminRepo.get_account_by_url(db, account_url)
            member = await MemberRepo.get_member_by_mobile_number(db, account.mobile_number)
            member_user_id = member.member_id

            if not account:
                return json_response(
                    message="Invalid username or password",
                    status_code=401
                )

            if account.username != login_data.username:
                return json_response(
                    message="Invalid username or password",
                    status_code=401
                )
            
            if not verify_password(login_data.password, account.password):
                return json_response(
                    message="Invalid username or password",
                    status_code=401
                )

            access_token = sign_jwt(account.id, account.account_type, member_user_id)["access_token"]
                    
            return {"message": "Login successful", "access_token": access_token, "account_type": account.account_type, "member_user_id": member_user_id}

        
        except Exception as e:
            logger.error("Error during login: %s", str(e))



    @staticmethod
    async def get_all_accounts(db: AsyncSession):
        try:
            accounts = await AdminRepo.get_all_accounts(db)
            return accounts
        except Exception as e:
            logger.error("Error retrieving accounts: %s", str(e))
            return json_response(
                status_code=500,
                message="An error occurred while fetching accounts.",
                data=None
            )
        


    @staticmethod
    async def initiate_member_activation(db: AsyncSession, activated_by: str):
        from api.v1.services.TopWallet import TopWallet
        try:
            response_data = await TopWallet.initiate_member_activation(db, activated_by)

            return json_response(
                message="Member activation initiated successfully",
                data=response_data,
                status_code=200
            )
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            logger.error("Unexpected error while initiating member activation", exc_info=True)


    @staticmethod
    async def process_member_activation(db: AsyncSession, activation_data: dict, activated_by: str):

        try:
            response_data = await TopWallet.process_member_activation(activation_data)
            # Fetch unilevel referrers
            unilevels = await MemberRepo.get_member_unilevel(db, activation_data.member_id)

            print("response_dataaa", response_data)
            activation_history = ActivationHistory(
                member_id=activation_data.member_id,
                activated_by=activated_by,
                reference_id = response_data["success"],
                amount = 175,
                status = response_data["status"],
                currency = "peso"
            )

            # Reward mapping (Unilevel Rewards)
            unilevel_rewards = {
                "first_level": 40,  # Level 1 reward
                "second_level": 10,  # Level 2 reward
                "third_level": 5    # Level 3 reward
            }

            # Store rewards for each unique upline
            reward_entries = []

            # Process rewards for each upline (Levels 1-3)
            for level, upline_id in unilevels.items():
                if upline_id:
                    reward_points = unilevel_rewards[level]

                    # Get the upline's current reward points
                    current_points = await MemberRepo.get_reward_points(db, upline_id)
                    new_total_points = current_points + reward_points

                    # Update the upline's wallet reward points
                    await db.execute(
                        Wallet.__table__.update()
                        .where(Wallet.wallet_id == select(MemberWallet.wallet_id).where(MemberWallet.member_id == upline_id).scalar_subquery())
                        .values(reward_points=new_total_points)
                    )

                    # Add reward entry
                    reward_entries.append(Reward(
                        reward_source_type="Member Activation",
                        reward_points=reward_points,
                        reward_from=activation_data.member_id,
                        receiver=upline_id,
                        title=f"Unilevel {level.replace('_', ' ').title()} Reward",
                        description="Reward for successfully activating a member",
                        status=response_data["status"],
                        reference_id=response_data["success"]
                    ))


            member = await MemberRepo.get_member_by_id(db, activation_data.member_id)

            # Process activator reward
            activator_reward_points = 25  # Activator gets 25 reward points

            # Get the activator's current reward points
            activator_current_points = await MemberRepo.get_reward_points(db, activated_by)
            activator_new_total = activator_current_points + activator_reward_points

            # Update the activator's wallet reward points
            await db.execute(
                Wallet.__table__.update()
                .where(Wallet.wallet_id == select(MemberWallet.wallet_id)
                    .where(MemberWallet.member_id == activated_by)
                    .scalar_subquery())
                .values(reward_points=activator_new_total)
            )

            # Create activator reward entry
            activator_reward = Reward(
                reward_source_type="Member Activation",
                reward_points=activator_reward_points,
                reward_from=activation_data.member_id,
                receiver=activated_by,
                title="Activator Reward",
                description="Reward for successfully activating a member",
                status=response_data["status"],
                reference_id=response_data["success"]
            )

            member.is_activated = True

            # Save all rewards
            db.add(activator_reward)
            db.add_all(reward_entries)
            db.add(member)
            db.add(activation_history)
            await db.commit()
            await db.refresh(activation_history)

            return json_response(
                message="Member activation processed successfully",
                data=response_data,
                status_code=200
            )


        except HTTPException as e:
            await db.rollback()
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            await db.rollback()
            logger.error("Unexpected error while processing member activation", exc_info=True)



