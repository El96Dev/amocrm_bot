from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserCredentials, UserTokens


async def get_user_credentials(session: AsyncSession) -> UserCredentials | None:
    stmt = select(UserCredentials)
    result = await session.execute(stmt)
    credentials = result.scalars().one_or_none()
    return credentials


async def set_user_credentials(chat_id: int, client_id: str, secret_key: str, redirect_url: str, 
                               subdomain: str, auth_code: str, session: AsyncSession) -> UserCredentials:
    stmt = select(UserCredentials).where(UserCredentials.chat_id==chat_id)
    result = await session.execute(stmt)
    user_credentials = result.scalars().one_or_none()
    if user_credentials is not None:
        user_credentials.client_id = client_id
        user_credentials.secret_key = secret_key
        user_credentials.redirect_url = redirect_url
        user_credentials.subdomain = subdomain
        user_credentials.auth_code = auth_code
        await session.commit()
        return user_credentials
    else:
        user_credentials = UserCredentials(chat_id=chat_id, client_id=client_id, secret_key=secret_key, 
                                           redirect_url=redirect_url, subdomain=subdomain, auth_code=auth_code)
        session.add(user_credentials)
        await session.commit()
        return user_credentials


async def get_user_tokens(session: AsyncSession) -> UserTokens | None:
    stmt = select(UserTokens)
    result = await session.execute(stmt)
    tokens = result.scalars().one_or_none()
    return tokens


async def set_user_tokens(chat_id: int, access_token: str, refresh_token: str, session: AsyncSession) -> UserTokens:
    stmt = select(UserTokens).where(UserTokens.chat_id==chat_id)
    result = await session.execute(stmt)
    user_tokens = result.scalars().one_or_none()
    if user_tokens is not None:
        user_tokens.access_token = access_token
        user_tokens.refresh_token = refresh_token
        await session.commit()
        return user_tokens
    else:
        user_tokens = UserTokens(chat_id=chat_id, access_token=access_token, refresh_token=refresh_token)
        session.add(user_tokens)
        await session.commit()
        return user_tokens
    