# بموووت ضحك 😹
from telethon import functions
from telethon.errors import ChatAdminRequiredError, UserAlreadyInvitedError
from telethon.tl.types import Channel, Chat, User
from zthon import zedub
from zthon.core.managers import edit_delete, edit_or_reply
from zthon.helpers.utils import mentionuser

plugin_category = "extra"


async def get_group_call(chat):
    if isinstance(chat, Channel):
        result = await zedub(functions.channels.GetFullChannelRequest(channel=chat))
    elif isinstance(chat, Chat):
        result = await zedub(functions.messages.GetFullChatRequest(chat_id=chat.id))
    return result.full_chat.call


async def chat_vc_checker(event, chat, edits=True):
    if isinstance(chat, User):
        await edit_delete(event, "Voice Chats are not available in Private Chats")
        return None
    result = await get_group_call(chat)
    if not result:
        if edits:
            await edit_delete(event, "No Group Call in this chat")
        return None
    return result


async def parse_entity(entity):
    if entity.isnumeric():
        entity = int(entity)
    return await zedub.get_entity(entity)


@zedub.zed_cmd(
    pattern="افتح الكول",
    command=("افتح الكول", plugin_category),
    info={
        "header": "To end a stream on Voice Chat.",
        "description": "To end a stream on Voice Chat",
        "usage": "{tr}vcstart",
        "examples": "{tr}vcstart",
    },
)
async def start_vc(event):
    "To start a Voice Chat."
    vc_chat = await zedub.get_entity(event.chat_id)
    gc_call = await chat_vc_checker(event, vc_chat, False)
    if gc_call:
        return await edit_delete(event, "Group Call is already available in this chat")
    try:
        await zedub(
            functions.phone.CreateGroupCallRequest(
                peer=vc_chat,
                title="سورس كرستين",
            )
        )
        await edit_delete(event, "Started Group Call")
    except ChatAdminRequiredError:
        await edit_delete(event, "You should be chat admin to start vc", time=20)


@zedub.zed_cmd(
    pattern="اقفل الكول",
    command=("اقفل الكول", plugin_category),
    info={
        "header": "To end a stream on Voice Chat.",
        "description": "To end a stream on Voice Chat",
        "usage": "{tr}vcend",
        "examples": "{tr}vcend",
    },
)
async def end_vc(event):
    "To end a Voice Chat."
    vc_chat = await zedub.get_entity(event.chat_id)
    gc_call = await chat_vc_checker(event, vc_chat)
    if not gc_call:
        return
    try:
        await zedub(functions.phone.DiscardGroupCallRequest(call=gc_call))
        await edit_delete(event, "تم قفݪ أݪڪۅٛݪ")
    except ChatAdminRequiredError:
        await edit_delete(event, "لازم تكون ادمن عشان تقفل الكول", time=20)


@zedub.zed_cmd(
    pattern="دعوة ?(.*)?",
    command=("دعوة", plugin_category),
    info={
        "header": "To invite users on Voice Chat.",
        "usage": "{tr}vcinv < userid/username or reply to user >",
        "examples": [
            "{tr}vcinv @angelpro",
            "{tr}vcinv userid1 userid2",
        ],
    },
)
async def inv_vc(event):
    "To invite users to vc."
    users = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    vc_chat = await zedub.get_entity(event.chat_id)
    gc_call = await chat_vc_checker(event, vc_chat)
    if not gc_call:
        return
    if not users:
        if not reply:
            return await edit_delete("عاوزني اعمل دعوه لمين")
        users = reply.from_id
    await edit_or_reply(event, "عملته دعوه خلاص اهو")
    entities = str(users).split(" ")
    user_list = []
    for entity in entities:
        cc = await parse_entity(entity)
        if isinstance(cc, User):
            user_list.append(cc)
    try:
        await zedub(
            functions.phone.InviteToGroupCallRequest(call=gc_call, users=user_list)
        )
        await edit_delete(event, "عملته دعوه خلاص اهو")
    except UserAlreadyInvitedError:
        return await edit_delete(event, "معموله دعوه", time=20)


@zedub.zed_cmd(
    pattern="مين في الكول",
    command=("مين في الكول", plugin_category),
    info={
        "header": "To get info of Voice Chat.",
        "usage": "{tr}vcinfo",
        "examples": "{tr}vcinfo",
    },
)
async def info_vc(event):
    "Get info of VC."
    vc_chat = await zedub.get_entity(event.chat_id)
    gc_call = await chat_vc_checker(event, vc_chat)
    if not gc_call:
        return
    await edit_or_reply(event, "هطلع اشوفلك مين")
    call_details = await zedub(
        functions.phone.GetGroupCallRequest(call=gc_call, limit=1)
    )
    grp_call = "**معلومات المكالمه**\n\n"
    grp_call += f"**العنوان :** {call_details.call.title}\n"
    grp_call += f"**عددهمt :** {call_details.call.participants_count}\n\n"

    if call_details.call.participants_count > 0:
        grp_call += "**ال في كول**\n"
        for user in call_details.users:
            nam = f"{user.first_name or ''} {user.last_name or ''}"
            grp_call += f"  ● {mentionuser(nam,user.id)} - `{user.id}`\n"
    await edit_or_reply(event, grp_call)


@zedub.zed_cmd(
    pattern="عنوان",
    command=("عنوان", plugin_category),
    info={
        "header": "To get info of Voice Chat.",
        "usage": "{tr}vcinfo",
        "examples": "{tr}vcinfo",
    },
)
async def title_vc(event):
    "To change vc title."
    title = event.pattern_match.group(1)
    vc_chat = await zedub.get_entity(event.chat_id)
    gc_call = await chat_vc_checker(event, vc_chat)
    if not gc_call:
        return
    if not title:
        return await edit_delete("What should i keep as title")
    await zedub(functions.phone.EditGroupCallTitleRequest(call=gc_call, title=title))
    await edit_delete(event, f"VC title was changed to **{title}**")


@zedub.zed_cmd(
    pattern="vc(|un)mute ([\s\S]*)",
    command=("vcmute", plugin_category),
    info={
        "header": "To mute users on Voice Chat.",
        "description": "To mute a stream on Voice Chat",
        "usage": [
            "{tr}vcmute < userid/username or reply to user >",
        ],
        "examples": [
            "{tr}vcmute @angelpro",
            "{tr}vcmute userid1 userid2",
        ],
    },
)
async def mute_vc(event):
    "To mute users in vc."
    cmd = event.pattern_match.group(1)
    users = event.pattern_match.group(2)
    reply = await event.get_reply_message()
    vc_chat = await zedub.get_entity(event.chat_id)
    gc_call = await chat_vc_checker(event, vc_chat)
    if not gc_call:
        return
    check = "Unmute" if cmd else "Mute"
    if not users:
        if not reply:
            return await edit_delete(f"Whom Should i {check}")
        users = reply.from_id
    await edit_or_reply(event, f"{check[:-1]}ing User in Group Call")
    entities = str(users).split(" ")
    user_list = []
    for entity in entities:
        cc = await parse_entity(entity)
        if isinstance(cc, User):
            user_list.append(cc)

    for user in user_list:
        await zedub(
            functions.phone.EditGroupCallParticipantRequest(
                call=gc_call,
                participant=user,
                muted=bool(not cmd),
            )
        )
    await edit_delete(event, f"{check}d users in Group Call")


@zedub.zed_cmd(
    command=("vcunmute", plugin_category),
    info={
        "header": "To unmute users on Voice Chat.",
        "description": "To unmute a stream on Voice Chat",
        "usage": [
            "{tr}vcunmute < userid/username or reply to user>",
        ],
        "examples": [
            "{tr}vcunmute @angelpro",
            "{tr}vcunmute userid1 userid2",
        ],
    },
)
async def unmute_vc(event):
    "To unmute users in vc."
