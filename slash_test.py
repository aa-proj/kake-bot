# discord ライブラリをインポート
import discord
from discord.app_commands import Choice

# requestライブラリをインポート
import requests

import typing

import enum

# インテント(discordに何の情報が欲しいのかログインの時に伝える変数)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Discordクライアントを準備 インテントを引数に渡してる
client = discord.Client(intents=intents)

# コマンドツリーをログイン後に取得してる
tree = discord.app_commands.CommandTree(client)

# ギルド変数(鯖IDを変数に入れておく)
guild_target = discord.Object(id=606109479003750440)

def idtoname(id) :
    guild=client.get_guild(606109479003750440)
    gm = guild.members
    for m in gm:
        if id == m.id:
            return m.display_name

# ライブラリにイベントを登録 "on_ready"
# readyの時にDiscord側から実行される
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # コマンドツリーをシンク(同期する)
    await tree.sync(guild=guild_target)


gamelist = {} #keyにgamename、valueに{賭けた人idと賭け金int}の辞書を入れる
l = []

@tree.command(name='betsset', description='賭けを設定しよう', guild=guild_target) #賭けを設定する
async def betsset(interaction: discord.Integration, gamename:str):
    print("betsset command received")
    global gamelist
    global l
    if gamename not in gamelist:
        await interaction.response.send_message(f"賭け {gamename} が開始されました。`/bets`で賭けてください。")
        gamelist[gamename] = {'YES':{},'NO':{}}
        print(gamelist)
        i =0
        for k in list(gamelist):
            l = l + [
            Choice(name=k, value=i),]
            print(k,i)
            i +=1
        await tree.sync(guild=guild_target)
        return
    else:
        await interaction.response.send_message(f"賭け {gamename} はすでに開始されています。`/bets`で賭けてください。")
        return



# コマンド登録
@tree.command(name="bets", description="賭けをしよう", guild=guild_target) #賭けをする
@discord.app_commands.choices(yesno = [
    Choice(name='YES', value='y'),
    Choice(name='NO', value='n'),])

@discord.app_commands.choices(
    gamename = l)

async def bets(interaction: discord.Interaction, gamename:Choice[int] , yesno:Choice[str] , amount: int):
    # コマンドが呼ばれたときの処理
    print("bets command received")
    #銀行に残高を確認しに行く
    r = requests.get(f'https://bank.ahoaho.jp/{interaction.user.id}')
    print(f'https://bank.ahoaho.jp/{interaction.user.id}')
    print(r)
    print(r.json())
    bankbalance = r.json()

    global gamelist

    if bankbalance['success'] == False:
        await interaction.response.send_message(f" {idtoname(interaction.user.id)} はああ国営銀行に口座がないかも")
        return

    if amount <= 0:
        await interaction.response.send_message(f"amountには1以上の整数をいれてね！")
        return

    if amount >= bankbalance['amount']:
        await interaction.response.send_message(f" {idtoname(interaction.user.id)}!口座残高<{bankbalance['amount']}p>よりも高い金額は賭けれないよ！")
        return

    if gamename in gamelist:
        YNlist = gamelist[gamename] #gamelistにあるgamenameのY/Nの辞書を代入
        await interaction.response.send_message(f" {idtoname(interaction.user.id)} は {gamename} の {yesno.name} に {amount} P賭けました")
        print(f" {idtoname(interaction.user.id)} は {gamename} の {yesno.name} に {amount} P賭けました") #ターミナルに出してみる
        Ylist = YNlist['YES']
        Nlist = YNlist['NO'] #YとNのリストを出す

        if (interaction.user.id not in Ylist) and (interaction.user.id not in Nlist): #YにもNにも賭けてなかったら
            if yesno.name == 'YES': #Yに賭けるなら
                Ylist[interaction.user.id] = amount #Ylistにidを追加
                return

            if yesno.name == 'NO':#Nに賭けるなら
                Nlist[interaction.user.id] = amount #Nlistにidを追加
                return

        if interaction.user.id in YNlist['YES']: #既にYESに賭けていたら
            if yesno.name == 'YES': #追加でYに賭けるなら
                amount = Ylist[interaction.user.id] + amount
                Ylist[interaction.user.id] = amount

                if interaction.user.id in YNlist['NO']: #Nにも賭けているなら
                    print(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました") #ターミナルに出してみる
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました")
                    print(gamelist)
                    return
                else:
                    print(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P賭けました") #ターミナルに出してみる
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} に {Ylist[interaction.user.id]}P賭けました")
                    print(gamelist)
                    return

            if yesno.name == 'NO': #追加でNに賭けるなら
                if interaction.user.id not in Nlist:
                    Nlist[interaction.user.id] = amount #Nlistにidを追加
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました")
                    return
                else:
                    amount = Nlist[interaction.user.id] + amount
                    Nlist[interaction.user.id] = amount
                    print(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました") #ターミナルに出してみる
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました")
                    print(gamelist)
                    return

        if interaction.user.id in YNlist['NO']: #既にNOに賭けていたら
            if yesno.name == 'YES': #追加でYに賭けるなら
                if interaction.user.id not in Ylist:
                    Ylist[interaction.user.id] = amount #Ylistにidを追加
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました")
                    return
                else:
                    amount = Ylist[interaction.user.id] + amount
                    Ylist[interaction.user.id] = amount
                    print(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました") #ターミナルに出してみる
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました")
                    print(gamelist)
                    return

            if yesno.name == 'NO': #追加でNに賭けるなら
                amount = Nlist[interaction.user.id] + amount
                Nlist[interaction.user.id] = amount

                if interaction.user.id in YNlist['YES']: #Yにも賭けているなら
                    print(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました") #ターミナルに出してみる
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のYESに {Ylist[interaction.user.id]}P、NOに {Nlist[interaction.user.id]}P賭けました")
                    print(gamelist)
                    return
                else:
                    print(f" {idtoname(interaction.user.id)}は合計 {gamename} のNOに {Nlist[interaction.user.id]}P賭けました") #ターミナルに出してみる
                    await interaction.channel.send(f" {idtoname(interaction.user.id)}は合計 {gamename} のNOに {Nlist[interaction.user.id]}P賭けました")
                    print(gamelist)
                    return

@tree.command(name="betslists", description="現在進行中の賭けの一覧を出します", guild=guild_target) #賭けの一覧をだす
async def betslists(interaction: discord.Interaction):
    if len(gamelist) == 0:
        await interaction.response.send_message('誰も賭けてません')
    else:
        ichiran = '```'
        for k in gamelist.keys(): #gamenameを表示
            print(k)
            ichiran = ichiran + (f'\n【{k}】')
            YNlist = gamelist[k]

            for yn in YNlist.keys(): #Y or Nを表示
                ichiran = ichiran + (f'\n<{yn}>')
                YorNlist = YNlist[yn]

                ynsum = sum(YorNlist.values())
                ichiran = ichiran + (f'  {len(YorNlist)}人 合計 {ynsum} p')
                if yn == 'YES':
                    ysum = ynsum


                for n,p in YorNlist.items(): #displaynameとポイントのリストを表示
                    ichiran = ichiran + (f'\n{idtoname(n)}:{p}')
                    if yn =='NO':
                        yodds = float(ynsum/ysum)
                        nodds = float(ysum/ynsum)
                        ichiran = ichiran + (f'\n<オッズ> YES {round(yodds, 2)} 倍 : NO {round(nodds, 2)} 倍')

        await interaction.response.send_message(ichiran + '```')
        return

#勝者を確定させる
@tree.command(name='win', description='賭けの勝者を確定させます（気を付けて！）', guild=guild_target)
@discord.app_commands.choices(winner = [
    Choice(name='YES', value=1),
    Choice(name='NO', value=2),])
async def win(interaction: discord.Interaction, gamename:str, winner:Choice[int]):

    if gamename not in gamelist: #存在しないgamename
        await interaction.response.send_message(f"賭け {gamename} は存在しません。`/betslists`で賭け一覧を確認してください。")
        return
    
    YNlist = gamelist[gamename]
    if YNlist['YES'] == {} and YNlist['NO'] == {}: #賭けた人がいない
        await interaction.response.send_message(f"賭け {gamename} に賭けた人がいません。`/bets`で賭けてください。")
        return

    if YNlist['YES'] == {}: #Yに賭けた人がいない
        await interaction.response.send_message(f"賭け {gamename} のYESに賭けた人がいません。`/bets`で賭けてください。")
        return

    if YNlist['NO'] == {}: #Nに賭けた人がいない
        await interaction.response.send_message(f"賭け {gamename} のNOに賭けた人がいません。`/bets`で賭けてください。")
        return

    else:
        if winner.name == 'YES': #Yが勝利
            winlist = YNlist['YES']
            loselist = YNlist['NO']
            maketahito = ''
            kattahito = ''
            for n,p in loselist.items():
                maketahito = maketahito + (f'\n<@{n}>:{p}p')
            for k in winlist.keys():
                kattahito = kattahito +(f'\n<@{k}>')
            await interaction.response.send_message(f'【{gamename} 勝者`YES`】{kattahito} \n に {maketahito} \nを支払ってください')
            del gamelist[gamename]
            return
        if winner.name == 'NO':#Nが勝利
            winlist = YNlist['NO']
            loselist = YNlist['YES']
            maketahito = ''
            kattahito = ''
            for n,p in loselist.items():
                maketahito = maketahito + (f'\n<@{n}>:{p}p')
            for k in winlist.keys():
                kattahito = kattahito +(f'\n<@{k}>')
            await interaction.response.send_message(f'【{gamename} 勝者`NO`】{kattahito} \n に {maketahito} \nを支払ってください')
            del gamelist[gamename]
            return

#賭けをリセット
@tree.command(name='betsreset', description='賭けをリセットさせます（気を付けて！）', guild=guild_target)
async def betsreset(interaction: discord.Integration, gamename:str):
    if gamename not in gamelist:
        await interaction.response.send_message(f'{gamename} は存在しません')
        return

    else:
        del gamelist[gamename]
        await interaction.response.send_message(f'{gamename} がリセットされました')
        return


# DiscordにTokenでログインする
client.run('TOKEN')