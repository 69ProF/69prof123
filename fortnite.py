"""
“Commons Clause” License Condition v1.0
Copyright Oli 2019

The Software is provided to you by the Licensor under the
License, as defined below, subject to the following condition.

Without limiting other conditions in the License, the grant
of rights under the License will not include, and the License
does not grant to you, the right to Sell the Software.

For purposes of the foregoing, “Sell” means practicing any or
all of the rights granted to you under the License to provide
to third parties, for a fee or other consideration (including
without limitation fees for hosting or consulting/ support
services related to the Software), a product or service whose
value derives, entirely or substantially, from the functionality
of the Software. Any license notice or attribution required by
the License must also include this Commons Clause License
Condition notice.

Software: 69ProF

License: Apache 2.0
"""

try:
    # Standard library imports
    import asyncio
    import aiohttp
    import datetime
    import json
    import logging
    import sys
    import functools
    import os

    # Related third party imports
    import crayons
    import fortnitepy
    import fortnitepy.errors
    import BenBotAsync
except ModuleNotFoundError as e:
    print(e)
    print('Failed to import 1 or more modules, running "INSTALL PACKAGES.bat" might fix the issue, if not please create an issue or join the support server.')
    exit()

def time():
    return datetime.datetime.now().strftime('%H:%M:%S')

def get_device_auth_details():
    if os.path.isfile('device_auths.json'):
        with open('device_auths.json', 'r') as fp:
            return json.load(fp)
    return {}

def store_device_auth_details(email, details):
    existing = get_device_auth_details()
    existing[email] = details

    with open('device_auths.json', 'w') as fp:
        json.dump(existing, fp, sort_keys=False, indent=4)

async def setVTID(VTID):
    url = f'http://benbotfn.tk:8080/api/assetProperties?file=FortniteGame/Content/Athena/Items/CosmeticVariantTokens/{VTID}.uasset'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            fileLocation = await r.json()

            SkinCID = fileLocation['export_properties'][0]['cosmetic_item']
            VariantChanelTag = fileLocation['export_properties'][0]['VariantChanelTag']['TagName']
            VariantNameTag = fileLocation['export_properties'][0]['VariantNameTag']['TagName']

            VariantType = VariantChanelTag.split('Cosmetics.Variant.Channel.')[1].split('.')[0]

            VariantInt = int("".join(filter(lambda x: x.isnumeric(), VariantNameTag)))

            if VariantType == 'ClothingColor':
                return SkinCID, 'clothing_color', VariantInt
            else:
                return SkinCID, VariantType, VariantInt

print(crayons.cyan(f'[69ProF] [{time()}] 69ProF created by storm'))

with open('config.json') as f:
    data = json.load(f)
    
if data['debug'] is True:
    logger = logging.getLogger('fortnitepy.http')
    logger.setLevel(level=logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('\u001b[36m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
    logger.addHandler(handler)

    logger = logging.getLogger('fortnitepy.xmpp')
    logger.setLevel(level=logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('\u001b[35m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
    logger.addHandler(handler)
else:
    pass

device_auth_details = get_device_auth_details().get(data['email'], {})
client = fortnitepy.Client(
    auth=fortnitepy.AdvancedAuth(
        email=data['email'],
        password=data['password'],
        prompt_exchange_code=True,
        delete_existing_device_auths=True,
        **device_auth_details
    ),
    status=data['status'],
    platform=fortnitepy.Platform(data['platform']),
    default_party_member_config=[
        functools.partial(fortnitepy.ClientPartyMember.set_outfit, data['cid']),
        functools.partial(fortnitepy.ClientPartyMember.set_backpack, data['bid']),
        functools.partial(fortnitepy.ClientPartyMember.set_banner, icon=data['banner'], color=data['banner_colour'], season_level=data['level']),
        functools.partial(fortnitepy.ClientPartyMember.set_emote, data['eid']),
        functools.partial(fortnitepy.ClientPartyMember.set_battlepass_info, has_purchased=True, level=data['bp_tier'], self_boost_xp='0', friend_boost_xp='0')
    ]
)

@client.event
async def event_device_auth_generate(details, email):
    store_device_auth_details(email, details)

@client.event
async def event_ready():
    print(crayons.green(f'[69ProF] [{time()}] Sikeres inditas a kovetkezo nevvel: {client.user.display_name}.'))

    for pending in client.pending_friends:
        friend = await pending.accept() if data["friendaccept"] else await pending.decline()
        if isinstance(friend, fortnitepy.Friend):
            print(f"[69ProF] [{time()}] Barat felkeres elfogadva neki: {friend.display_name}.")
        else:
            print(f"[69ProF] [{time()}] Barat felkeres elutasitva neki: {pending.display_name}.")

@client.event
async def event_party_invite(invite):
   await invite.accept()
   print(f'[69ProF] [{time()}] Party meghivas elfogadva {invite.sender.display_name}.')

@client.event
async def event_friend_request(request):
    print(f"[69ProF] [{time()}] Barat felkeres erkezett tole: {request.display_name}.")

    if data['friendaccept']:
        await request.accept()
        print(f"[69ProF] [{time()}] Barat felkeres elfogadva neki: {request.display_name}.")
    else:
        await request.decline()
        print(f"[69ProF] [{time()}] Barat felkeres elutasitva neki: {request.display_name}.")

@client.event
async def event_party_member_join(member):
    await BenBotAsync.set_default_loadout(client, data, member)

@client.event
async def event_friend_message(message):
    args = message.content.split()
    split = args[1:]
    content = " ".join(split)

    print(f'[69ProF] [{time()}] {message.author.display_name}: {message.content}')

    if "!skin" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.TYPE, 'Outfit']
        )

        if cosmetic == None:
            print(' ')
            await message.reply(f"Nem talaltam ilyen skint: {content}.")
            print(f"[69ProF] [{time()}] Nem talaltam ilyen skint: {content}.")
        else:
            await message.reply(f'Skin beallitva: {cosmetic.id}.')
            print(f"[69ProF] [{time()}] Skin beallitva: {cosmetic.id}.")
            await client.user.party.me.set_outfit(asset=cosmetic.id)
        
    elif "!backpack" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.TYPE, 'Back Bling']
        )

        if cosmetic == None:
            await message.reply(f"Nem talaltam ilyen hatizsakot: {content}.")
            print(f"[69ProF] [{time()}] Nem talaltam ilyen hatizsakot: {content}.")
        else:
            await message.reply(f'Hatizsak beallitva: {cosmetic.id}.')
            print(f"[69ProF] [{time()}] Hatizsak beallitva: {cosmetic.id}.")
            await client.user.party.me.set_backpack(asset=cosmetic.id)

    elif "!emote" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.TYPE, 'Emote']
        )

        if cosmetic == None:
            await message.reply(f"Nem talalok ilyen tancot: {content}.")
            print(f"[69ProF] [{time()}] Nem talalok ilyen tancot: {content}.")
        else:
            await message.reply(f'Tanc beallitva: {cosmetic.displayName}.')
            print(f"[69ProF] [{time()}] Tanc beallitva: {cosmetic.displayName}.")
            await client.user.party.me.set_emote(asset=cosmetic.id)

    elif "!pickaxe" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.TYPE, 'Harvesting Tool']
        )

        if cosmetic == None:
            await message.reply(f"Nem talalok ilyen csakanyt: {content}.")
            print(f"[69ProF] [{time()}] Nem talalok ilyen csakanyt: {content}.")
        else:
            await message.reply(f'Csakany beallitva: {cosmetic.displayName}.')
            print(f"[69ProF] [{time()}] Csakany beallitva: {cosmetic.displayName}.")
            await client.user.party.me.set_pickaxe(asset=cosmetic.id)

    elif "!pet" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.BACKEND_TYPE, 'AthenaPet']
        )

        if cosmetic == None:
            await message.reply(f"Nem talalok ilyen kisallatot: {content}.")
            print(f"[69ProF] [{time()}] Nem talalok ilyen kisallatot: {content}.")
        else:
            await message.reply(f'Kisallat beallitva: {cosmetic.displayName}.')
            print(f"[69ProF] [{time()}] Kisallat beallitva: {cosmetic.displayName}.")
            await client.user.party.me.set_pet(asset=cosmetic.id)

    elif "!emoji" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.BACKEND_TYPE, 'AthenaDance']
        )

        if cosmetic == None:
            await message.reply(f"Nem talalok ilyen emojit: {content}.")
            print(f"[69ProF] [{time()}] Nem talalok ilyen emojit: {content}.")
        else:
            await message.reply(f'Emoji beallitva {cosmetic.id}.')
            print(f"[69ProF] [{time()}] Emoji beallitva: {cosmetic.id}.")
            await client.user.party.me.set_emoji(asset=cosmetic.id)

    elif "!contrail" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            filter=[BenBotAsync.Filters.TYPE, 'Contrail']
        )

        if cosmetic == None:
            await message.reply(f"Nem talalok ilyen esest: {content}.")
            print(f"[69ProF] [{time()}] Nem talalok ilyen esest: {content}.")
        else:
            await message.reply(f'Eses beallitva {cosmetic.id}.')
            print(f"[69ProF] [{time()}] Eses beallitva: {cosmetic.id}.")
            await client.user.party.me.set_contrail(cosmetic.id)

    elif "!lilaskull" in args[0].lower():
        variants = client.user.party.me.create_variants(
           clothing_color=1
        )

        await client.user.party.me.set_outfit(
            asset='CID_030_Athena_Commando_M_Halloween',
            variants=variants
        )

        await message.reply('Kinezet beallitva!')

    elif "!pinkghoul" in args[0].lower():
        variants = client.user.party.me.create_variants(
           material=3
        )

        await client.user.party.me.set_outfit(
            asset='CID_029_Athena_Commando_F_Halloween',
            variants=variants
        )

        await message.reply('Kinezet beallitva!')

    elif "!purpleportal" in args[0].lower():
        variants = client.user.party.me.create_variants(
            item='AthenaBackpack',
            particle_config='Particle',
            particle=1
        )

        await client.user.party.me.set_backpack(
            asset='BID_105_GhostPortal',
            variants=variants
        )

        await message.reply('Hatizsak beallitva!')

    elif "!banner" in args[0].lower():
        if len(args) == 1:
            await message.reply('Meg kell adnod a szinet, szamat!')
        elif len(args) == 2:
            await client.user.party.me.set_banner(icon=args[1], color=data['banner_colour'], season_level=data['level'])
        elif len(args) == 3:
            await client.user.party.me.set_banner(icon=args[1], color=args[2], season_level=data['level'])
        elif len(args) == 4:
            await client.user.party.me.set_banner(icon=args[1], color=args[2], season_level=args[3])
        else:
            await message.reply('Hiba!')

        await message.reply(f'Banner beallitva; {args[1]} {args[2]} {args[3]}')
        print(f"[69ProF] [{time()}] Banner beallitva; {args[1]} {args[2]} {args[3]}")

    elif "cid_" in args[0].lower():
        if 'banner' not in args[0]:
            await client.user.party.me.set_outfit(
                asset=args[0]
            )
        else:
            await client.user.party.me.set_outfit(
                asset=args[0],
                variants=client.user.party.me.create_variants(profilebanner='ProfileBanner')
            )

        await message.reply(f'Kinezet beallitva {args[0]}')
        await print(f'[69ProF] [{time()}] Kinezet beallitva {args[0]}')

    elif "vtid_" in args[0].lower():
        VTID = await setVTID(args[0])
        if VTID[1] == 'Particle':
            variants = client.user.party.me.create_variants(particle_config='Particle', particle=1)
        else:
            variants = client.user.party.me.create_variants(**{VTID[1].lower(): int(VTID[2])})

        await client.user.party.me.set_outfit(asset=VTID[0], variants=variants)
        await message.reply(f'Variants set to {args[0]}.\n(Warning: This feature is not supported, please use !variants)')

    elif "!variants" in args[0]:
        try:
            args3 = int(args[3])
        except ValueError:
            args3 = args[3]

        if 'cid' in args[1].lower() and 'jersey_color' not in args[2]:
            variants = client.user.party.me.create_variants(**{args[2]: args[3]})
            await client.user.party.me.set_outfit(
                asset=args[1],
                variants=variants
            )
        elif 'cid' in args[1].lower() and 'jersey_color' in args[2]:
            variants = client.user.party.me.create_variants(pattern=0, numeric=69, **{args[2]: args[3]})
            await client.user.party.me.set_outfit(
                asset=args[1],
                variants=variants
            )
        elif 'bid' in args[1].lower():
            variants = client.user.party.me.create_variants(item='AthenaBackpack', **{args[2]: args3})
            await client.user.party.me.set_backpack(
                asset=args[1],
                variants=variants
            )
        elif 'pickaxe_id' in args[1].lower():
            variants = client.user.party.me.create_variants(item='AthenaPickaxe', **{args[2]: args3})
            await client.user.party.me.set_pickaxe(
                asset=args[1],
                variants=variants
            )

        await message.reply(f'Set variants of {args[1]} to {args[2]} {args[3]}.')
        print(f'[69ProF] [{time()}] Set variants of {args[1]} to {args[2]} {args[3]}.')

    elif "!checkeredrenegade" in args[0].lower():
        variants = client.user.party.me.create_variants(
           material=2
        )

        await client.user.party.me.set_outfit(
            asset='CID_028_Athena_Commando_F',
            variants=variants
        )

        await message.reply('Kinezet beallitva Checkered Renegade!')

    elif "!mintyelf" in args[0].lower():
        variants = client.user.party.me.create_variants(
           material=2
        )

        await client.user.party.me.set_outfit(
            asset='CID_051_Athena_Commando_M_HolidayElf',
            variants=variants
        )

        await message.reply('Kinezet beallitva Minty Elf!')

    elif "eid_" in args[0].lower():
        await client.user.party.me.clear_emote()
        await client.user.party.me.set_emote(
            asset=args[0]
        )
        await message.reply(f'Tanc beallitva {args[0]}!')
        
    elif "!stop" in args[0].lower():
        await client.user.party.me.clear_emote()
        await message.reply('Tanc vege!')

    elif "bid_" in args[0].lower():
        await client.user.party.me.set_backpack(
            asset=args[0]
        )

        await message.reply(f'Hatizsak beallitva {args[0]}!')

    elif "!easteregg" in args[0].lower():
        await message.reply('Megtalaltad!')

    elif "PICKAXE_ID_" in args[0].lower():
        await client.user.party.me.set_pickaxe(
                asset=args[0]
        )

        await message.reply(f'Csakany beallitva {args[0]}')

    elif "petcarrier_" in args[0].lower():
        await client.user.party.me.set_pet(
                asset=args[0]
        )

        await message.reply(f'Kisallat beallitva {args[0]}!')

    elif "emoji_" in args[0].lower():
        await client.user.party.me.clear_emote()
        await client.user.party.me.set_emote(
                asset=args[0]
        )

        await message.reply(f'Emoji beallitva {args[0]}!')

    elif "trails_" in args[0].lower():
        await client.user.party.me.set_contrail(asset=args[0])

        await message.reply(f'Eses beallitva {args[0]}!')

    elif "!legacypickaxe" in args[0].lower():
        await client.user.party.me.set_pickaxe(
                asset=args[1]
        )

        await message.reply(f'Csakany beallitva {args[1]}!')

    elif "!point" in args[0].lower():
        if 'pickaxe_id' in args[1].lower():
            await client.user.party.me.set_pickaxe(asset=args[1])
            await client.user.party.me.set_emote(asset='EID_IceKing')
            await message.reply(f'Csakany beallitva {args[1]} Es Point it out tanc elinditva.')
        else:
            cosmetic = await BenBotAsync.get_cosmetic(content, params=BenBotAsync.Tags.NAME, filter=[BenBotAsync.Filters.TYPE, 'Harvesting Tool'])
            if cosmetic == None:
                await message.reply(f"Nem talalok ilyen csakanyt: {content}")
            else:
                await client.user.party.me.set_pickaxe(asset=cosmetic.id)
                await client.user.party.me.set_emote(asset='EID_IceKing')
                await message.reply(f'Csakany beallitva {content} Es Point it out tanc elinditva.')


    elif "!ready" in args[0].lower():
        await client.user.party.me.set_ready(fortnitepy.ReadyState.READY)
        await message.reply('Keszen allok!')

    elif ("!unready" in args[0].lower()) or ("!sitin" in args[0].lower()):
        await client.user.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await message.reply('Nem allok keszen!')

    elif "!sitout" in args[0].lower():
        await client.user.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await message.reply('Kialltam!')

    elif "!bp" in args[0].lower():
        await client.user.party.me.set_battlepass_info(has_purchased=True, level=args[1], self_boost_xp='0', friend_boost_xp='0')

    elif "!level" in args[0].lower():
        await client.user.party.me.set_banner(icon=client.user.party.me.banner[0], color=client.user.party.me.banner[1], season_level=args[1])

    elif "!echo" in args[0].lower():
        await client.user.party.send(content)

    elif "!status" in args[0].lower():
        await client.set_status(content)

        await message.reply(f'Statusz beallitva {content}')
        print(f'[69ProF] [{time()}] Statusz beallitva {content}.')

    elif "!leave" in args[0].lower():
        await client.user.party.me.set_emote('EID_Wave')
        await asyncio.sleep(2)
        await client.user.party.me.leave()
        await message.reply('Szia!')
        print(f'[69ProF] [{time()}] Kileptem mert azt akartak.')

    elif "!kick" in args[0].lower():
        user = await client.fetch_profile(content)
        member = client.user.party.members.get(user.id)
        if member is None:
            await message.reply("Nem talalok ilyen embert, biztosan jol irtad be?")
        else:
            try:
                await member.kick()
                await message.reply(f"Kirugott ember: {member.display_name}.")
                print(f"[69ProF] [{time()}] Kirugott ember: {member.display_name}")
            except fortnitepy.Forbidden:
                await message.reply(f"Nem tudom kirugni {member.display_name}, mert nem vagyok party leader.")
                print(crayons.red(f"[69ProF] [{time()}] [ERROR] Nem lehetseges."))

    elif "!promote" in args[0].lower():
        if len(args) != 1:
            user = await client.fetch_profile(content)
            member = client.user.party.members.get(user.id)
        if len(args) == 1:
            user = await client.fetch_profile(message.author.display_name)
            user = await client.user.party.members.get(user.id)

        if member is None:
            await message.reply("Nem talalom ot, biztosan jol irtad be a nevet?")
        else:
            try:
                await member.promote()
                await message.reply(f"Leader: {member.display_name}.")
                print(f"[69ProF] [{time()}] Leader: {member.display_name}")
            except fortnitepy.Forbidden:
                await message.reply(f"Nem tudom atadni a leadert {member.display_name}, mert nem en vagyok a party leader.")
                print(crayons.red(f"[69ProF] [{time()}] [ERROR] Nem lehetseges."))

    elif "playlist_" in args[0].lower():
        try:
            await client.user.party.set_playlist(playlist=args[0])
        except fortnitepy.Forbidden:
            await message.reply(f"Couldn't set gamemode to {args[1]}, as I'm not party leader.")
            print(crayons.red(f"[69ProF] [{time()}] [ERROR] Failed to set gamemode as I don't have the required permissions."))

    elif "!platform" in args[0].lower():
        await message.reply(f'Platform beallitva {args[0]}')
        party_id = client.user.party.id
        await client.user.party.me.leave()
        client.platform = fortnitepy.Platform(args[1])
        await message.reply(f'Platform mostantol {str(client.platform)}.')
        try:
            await client.join_to_party(party_id, check_private=True)
        except fortnitepy.Forbidden:
            await message.reply('Nem tudok csatlakozni a partyba mert privat.')

    elif args[0].lower() == "!id":
        user = await client.fetch_profile(content, cache=False, raw=False)
        try:
            await message.reply(f"{content} Epic ID-je: {user.id}")
        except AttributeError:
            await message.reply(f"Nem talalok ilyen embert: {content}.")

    elif "!privacy" in args[0].lower():
        try:
            if 'public' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            elif 'private' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
            elif 'friends' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.FRIENDS)
            elif 'friends_allow_friends_of_friends' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.FRIENDS_ALLOW_FRIENDS_OF_FRIENDS)
            elif 'private_allow_friends_of_friends' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE_ALLOW_FRIENDS_OF_FRIENDS)

            await message.reply(f'{client.user.party.privacy}.')
            print(f'[69ProF] [{time()}] {client.user.party.privacy}.')

        except fortnitepy.Forbidden:
            await message.reply(f"Couldn't set party privacy to {args[1]}, as I'm not party leader.")
            print(crayons.red(f"[69ProF] [{time()}] [ERROR] Failed to set party privacy as I don't have the required permissions."))

    elif "!copy" in args[0].lower():
        if len(args) >= 1:
            member = client.user.party.members.get(message.author.id)
        else:
            user = await client.fetch_profile(content)
            member = client.user.party.members.get(user.id)

        await client.user.party.me.edit(
            functools.partial(fortnitepy.ClientPartyMember.set_outfit, asset=member.outfit, variants=member.outfit_variants),
            functools.partial(fortnitepy.ClientPartyMember.set_backpack, asset=member.backpack, variants=member.backpack_variants),
            functools.partial(fortnitepy.ClientPartyMember.set_pickaxe, asset=member.pickaxe, variants=member.pickaxe_variants),
            functools.partial(fortnitepy.ClientPartyMember.set_banner, icon=member.banner[0], color=member.banner[1], season_level=member.banner[2]),
            functools.partial(fortnitepy.ClientPartyMember.set_battlepass_info, has_purchased=True, level=member.battlepass_info[1], self_boost_xp='0', friend_boost_xp='0')
        )

        await client.user.party.me.set_emote(asset=member.emote)

    elif "!hologram" in args[0].lower():
        await client.user.party.me.set_outfit(
            asset='CID_VIP_Athena_Commando_M_GalileoGondola_SG'
        )

        await message.reply('Kinezet beallitva Star Wars Hologram!')

if (data['email'] and data['password']) and (data['email'] != 'email@email.com' and data['password'] != 'password1'):
    try:
        client.run()
    except fortnitepy.AuthException as e:
        print(crayons.red(f"[69ProF] [{time()}] [ERROR] {e}"))
else:
    print(crayons.red(f"[69ProF] [{time()}] [ERROR] Nem tudok bejelentkezni."))
