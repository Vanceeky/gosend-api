from fastapi import APIRouter


from api.v1.routes import admin_routes as admin
from api.v1.routes import member_routes as members
from api.v1.routes import merchant_routes as merchants
from api.v1.routes import auth_routes as auth
from api.v1.routes import community_routes as community
from api.v1.routes import hub_routes as hub
from api.v1.routes import investor_routes as investor
from api.v1.routes import reward_routes as rewards


router = APIRouter()


router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(members.router, prefix="/member", tags=["members"])
router.include_router(merchants.router, prefix="/merchant", tags=["merchant"] )
router.include_router(community.router, prefix="/community", tags=["community"])
router.include_router(hub.router, prefix="/hub", tags=["hubs"])
router.include_router(investor.router, prefix="/investor", tags=["investor"])
router.include_router(rewards.router, prefix="/reward", tags=["reward"])
