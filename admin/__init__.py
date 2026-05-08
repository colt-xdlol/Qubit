from aiogram import Router

from admin import navigation, moderation_flow, outreach, snapshots


def build_admin_router() -> Router:
    root = Router()
    root.include_router(navigation.router)
    root.include_router(snapshots.router)
    root.include_router(outreach.router)
    root.include_router(moderation_flow.router)
    return root
