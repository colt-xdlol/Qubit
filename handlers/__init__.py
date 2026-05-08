from aiogram import Router

from handlers import (
    ai_question,
    business_auto_reply,
    chats,
    faq_support,
    menu_cmds,
    payments,
    referrals_info,
    start_user,
    usage_status,
)


def build_user_router() -> Router:
    root = Router()
    root.include_router(start_user.router)
    root.include_router(menu_cmds.router)
    root.include_router(chats.router)
    root.include_router(faq_support.router)
    root.include_router(usage_status.router)
    root.include_router(referrals_info.router)
    root.include_router(payments.router)
    root.include_router(business_auto_reply.router)
    root.include_router(ai_question.router)
    return root
