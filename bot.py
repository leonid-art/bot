# Telegram Casino Bot
import logging, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8786347236:AAF8ITVAoAh7qrN6i9h0_NoWMNAuPrGgKok"
STARTING_BALANCE = 1000
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)

def get_balance(ctx): return ctx.user_data.setdefault("balance", STARTING_BALANCE)
def add_balance(ctx, n): ctx.user_data["balance"] = get_balance(ctx) + n; return ctx.user_data["balance"]

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Blackjack", callback_data="bj_menu")],
        [InlineKeyboardButton("Coin Flip", callback_data="coin_menu")],
        [InlineKeyboardButton("Balance",   callback_data="balance")],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    bal = get_balance(ctx)
    txt = f"Casino!\n\nBalance: {bal}\n\nChoose:"
    if update.message: await update.message.reply_text(txt, reply_markup=main_menu())
    else: await update.callback_query.edit_message_text(txt, reply_markup=main_menu())

async def show_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(f"Balance: {get_balance(ctx)}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="menu")]]))

RANKS=["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
SUITS=["S","H","D","C"]
VAL={"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":10,"Q":10,"K":10,"A":11}

def new_deck():
    d=[(r,s) for r in RANKS for s in SUITS]; random.shuffle(d); return d

def hval(h):
    v=sum(VAL[r] for r,_ in h); a=sum(1 for r,_ in h if r=="A")
    while v>21 and a: v-=10; a-=1
    return v

def hstr(h, hide=False):
    if hide: return f"{h[0][0]}{h[0][1]} [?]"
    return " ".join(f"{r}{s}" for r,s in h)

BETS=[50,100,200,500]

async def bj_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    bal=get_balance(ctx)
    btns=[[InlineKeyboardButton(f"{b} coins", callback_data=f"bj_{b}")] for b in BETS if b<=bal]
    btns.append([InlineKeyboardButton("Back", callback_data="menu")])
    await q.edit_message_text(f"Blackjack\nBalance: {bal}\nBet:", reply_markup=InlineKeyboardMarkup(btns))

async def bj_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    bet=int(q.data.split("_")[1])
    if bet>get_balance(ctx): await q.answer("Not enough!", show_alert=True); return
    add_balance(ctx,-bet); ctx.user_data["bet"]=bet
    dk=new_deck(); pl=[dk.pop(),dk.pop()]; dl=[dk.pop(),dk.pop()]
    ctx.user_data.update({"dk":dk,"pl":pl,"dl":dl})
    if hval(pl)==21: await bj_end(q,ctx); return
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("Hit",callback_data="bj_hit"),InlineKeyboardButton("Stand",callback_data="bj_stand")]])
    await q.edit_message_text(f"Bet:{bet} Bal:{get_balance(ctx)}\nYou: {hstr(pl)} ({hval(pl)})\nDealer: {hstr(dl,True)}",reply_markup=kb)

async def bj_hit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    ctx.user_data["pl"].append(ctx.user_data["dk"].pop())
    pl=ctx.user_data["pl"]; bet=ctx.user_data["bet"]
    if hval(pl)>=21: await bj_end(q,ctx); return
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("Hit",callback_data="bj_hit"),InlineKeyboardButton("Stand",callback_data="bj_stand")]])
# Telegram Casino Bot
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN        = "8786347236:AAF8ITVAoAh7qrN6i9h0_NoWMNAuPrGgKok"
STARTING_BALANCE = 10000

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)


def get_balance(context):
    return context.user_data.setdefault("balance", STARTING_BALANCE)

def add_balance(context, amount):
    context.user_data["balance"] = get_balance(context) + amount
    return context.user_data["balance"]


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🃏 Блэкджек",   callback_data="bj_bet_menu")],
        [InlineKeyboardButton("🪙 Орёл-решка", callback_data="coin_bet_menu")],
        [InlineKeyboardButton("💰 Мой баланс", callback_data="show_balance")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for key in ("bj_hand","bj_dealer","bj_bet","bj_deck","coin_bet"):
        context.user_data.pop(key, None)
    bal  = get_balance(context)
    text = f"🎰 Добро пожаловать в казино!\n\n💰 Баланс: {bal} монет\n\nВыбери игру 👇"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard())


async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bal = get_balance(context)
    await query.edit_message_text(
        f"💰 Баланс: {bal} монет",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")]]),
    )


# ── БЛЭКДЖЕК ──────────────────────────────────────────────────

RANKS  = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
SUITS  = ["♠","♥","♦","♣"]
VALUES = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":10,"Q":10,"K":10,"A":11}

def new_deck():
    deck = [(r,s) for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

def draw(deck): return deck.pop()

def hand_value(hand):
    val  = sum(VALUES[r] for r,_ in hand)
    aces = sum(1 for r,_ in hand if r=="A")
    while val > 21 and aces:
        val -= 10; aces -= 1
    return val

def hand_str(hand, hide=False):
    if hide: return f"{hand[0][0]}{hand[0][1]}  🂠"
    return "  ".join(f"{r}{s}" for r,s in hand)

BJ_BETS = [50, 100, 200, 500]

def bj_bet_keyboard(bal):
    buttons = [[InlineKeyboardButton(f"💵 {b} монет", callback_data=f"bj_bet_{b}")] for b in BJ_BETS if b <= bal]
    buttons.append([InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def bj_game_keyboard(can_double=False):
    rows = [[InlineKeyboardButton("➕ Ещё", callback_data="bj_hit"),
             InlineKeyboardButton("✋ Стоп", callback_data="bj_stand")]]
    if can_double:
        rows.append([InlineKeyboardButton("✌️ Удвоить", callback_data="bj_double")])
    rows.append([InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


async def bj_bet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bal = get_balance(context)
    if bal < min(BJ_BETS):
        await query.edit_message_text("😔 Недостаточно монет.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")]]))
        return
    await query.edit_message_text(f"🃏 Блэкджек\n\n💰 Баланс: {bal} монет\nВыбери ставку:",
                                  reply_markup=bj_bet_keyboard(bal))


async def bj_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bet = int(query.data.split("_")[-1])
    bal = get_balance(context)
    if bet > bal:
        await query.answer("Недостаточно монет!", show_alert=True); return
    add_balance(context, -bet)
    context.user_data["bj_bet"] = bet
    deck   = new_deck()
    player = [draw(deck), draw(deck)]
    dealer = [draw(deck), draw(deck)]
    context.user_data.update({"bj_deck": deck, "bj_hand": player, "bj_dealer": dealer})
    if hand_value(player) == 21:
        await bj_resolve(query, context); return
    pval = hand_value(player)
    text = (f"🃏 Блэкджек  |  Ставка: {bet}\n💰 Баланс: {get_balance(context)}\n\n"
            f"Ты:    {hand_str(player)}  ({pval})\nДилер: {hand_str(dealer, hide=True)}")
    await query.edit_message_text(text, reply_markup=bj_game_keyboard(get_balance(context) >= bet))


async def bj_hit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    player = context.user_data["bj_hand"]
    player.append(draw(context.user_data["bj_deck"]))
    pval = hand_value(player)
    bet  = context.user_data["bj_bet"]
    if pval >= 21:
        await bj_resolve(query, context); return
    text = (f"🃏 Блэкджек  |  Ставка: {bet}\n💰 Баланс: {get_balance(context)}\n\n"
            f"Ты:    {hand_str(player)}  ({pval})\nДилер: {hand_str(context.user_data['bj_dealer'], hide=True)}")
    await query.edit_message_text(text, reply_markup=bj_game_keyboard())


async def bj_stand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await bj_resolve(update.callback_query, context, stood=True)


async def bj_double(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bet = context.user_data["bj_bet"]
    if get_balance(context) < bet:
        await query.answer("Недостаточно монет!", show_alert=True); return
    add_balance(context, -bet)
    context.user_data["bj_bet"] = bet * 2
    context.user_data["bj_hand"].append(draw(context.user_data["bj_deck"]))
    await bj_resolve(query, context, stood=True)


async def bj_resolve(query, context, stood=False):
    player = context.user_data["bj_hand"]
    dealer = context.user_data["bj_dealer"]
    deck   = context.user_data["bj_deck"]
    bet    = context.user_data["bj_bet"]
    pval   = hand_value(player)
    if stood:
        while hand_value(dealer) < 17:
            dealer.append(draw(deck))
    dval = hand_value(dealer)
    if pval > 21:
        outcome, delta = "💥 Перебор — проигрыш.", 0
    elif pval == 21 and len(player) == 2:
        outcome, delta = "🎉 Блэкджек! Выигрыш x2.5!", int(bet * 2.5)
    elif dval > 21:
        outcome, delta = "🏆 Дилер перебрал — победа!", bet * 2
    elif pval > dval:
        outcome, delta = "🏆 Победа!", bet * 2
    elif pval == dval:
        outcome, delta = "🤝 Ничья — ставка возвращена.", bet
    else:
        outcome, delta = "😞 Дилер выиграл.", 0
    add_balance(context, delta)
    bal    = get_balance(context)
    profit = delta - bet
    ps     = f"+{profit}" if profit > 0 else str(profit)
    text   = (f"🃏 Блэкджек — итог\n\n"
              f"Ты:    {hand_str(player)}  ({pval})\n"
              f"Дилер: {hand_str(dealer)}  ({dval})\n\n"
              f"{outcome}\nСтавка: {bet}  |  {ps} монет\n💰 Баланс: {bal}")
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Ещё раз", callback_data="bj_bet_menu")],
        [InlineKeyboardButton("⬅️ В меню",  callback_data="main_menu")],
    ]))


# ── ОРЁЛ-РЕШКА ────────────────────────────────────────────────

COIN_BETS = [50, 100, 200, 500]

def coin_bet_keyboard(bal):
    buttons = [[InlineKeyboardButton(f"💵 {b} монет", callback_data=f"coin_bet_{b}")] for b in COIN_BETS if b <= bal]
    buttons.append([InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


async def coin_bet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bal = get_balance(context)
    if bal < min(COIN_BETS):
        await query.edit_message_text("😔 Недостаточно монет.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ В меню", callback_data="main_menu")]]))
        return
    await query.edit_message_text(f"🪙 Орёл-решка\n\n💰 Баланс: {bal} монет\nВыбери ставку:",
                                  reply_markup=coin_bet_keyboard(bal))


async def coin_set_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bet = int(query.data.split("_")[-1])
    if bet > get_balance(context):
        await query.answer("Недостаточно монет!", show_alert=True); return
    context.user_data["coin_bet"] = bet
    await query.edit_message_text(
        f"🪙 Орёл-решка  |  Ставка: {bet} монет\n\nЧто выпадет?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🦅 Орёл",  callback_data="coin_heads"),
             InlineKeyboardButton("🔤 Решка", callback_data="coin_tails")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="coin_bet_menu")],
        ]),
    )


async def coin_flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    bet   = context.user_data.get("coin_bet", 0)
    guess = query.data
    if bet > get_balance(context):
        await query.answer("Недостаточно монет!", show_alert=True); return
    add_balance(context, -bet)
    result = random.choice(["coin_heads", "coin_tails"])
    rl = "🦅 Орёл" if result == "coin_heads" else "🔤 Решка"
    gl = "🦅 Орёл" if guess  == "coin_heads" else "🔤 Решка"
    if guess == result:
        delta, outcome = bet * 2, f"✅ Выпало {rl} — победа!"
    else:
        delta, outcome = 0, f"❌ Выпало {rl} — проигрыш."
    add_balance(context, delta)
    bal    = get_balance(context)
    profit = delta - bet
    ps     = f"+{profit}" if profit > 0 else str(profit)
    text   = (f"🪙 Орёл-решка\n\nТвой выбор: {gl}\n{outcome}\n\n"
              f"Ставка: {bet}  |  {ps} монет\n💰 Баланс: {bal}")
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Ещё раз", callback_data="coin_bet_menu")],
        [InlineKeyboardButton("⬅️ В меню",  callback_data="main_menu")],
    ]))


# ── РОУТЕР ────────────────────────────────────────────────────

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if   data == "main_menu":               await start(update, context)
    elif data == "show_balance":            await show_balance(update, context)
    elif data == "bj_bet_menu":             await bj_bet_menu(update, context)
    elif data.startswith("bj_bet_"):        await bj_start(update, context)
    elif data == "bj_hit":                  await bj_hit(update, context)
    elif data == "bj_stand":               await bj_stand(update, context)
    elif data == "bj_double":              await bj_double(update, context)
    elif data == "coin_bet_menu":           await coin_bet_menu(update, context)
    elif data.startswith("coin_bet_"):      await coin_set_bet(update, context)
    elif data in ("coin_heads","coin_tails"): await coin_flip(update, context)


# ── ЗАПУСК ────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))
    print("Бот запущен. Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()