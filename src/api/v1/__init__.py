from fastapi import APIRouter


from api.v1.routes import member_routes as members


router = APIRouter()



router.include_router(members.router, prefix="/members", tags=["members"])
