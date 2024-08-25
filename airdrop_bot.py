from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from db import (
    add_user, get_balance, update_balance, set_withdrawal_address, get_withdrawal_address,
    add_referral, is_referred, claim_daily_bonus, withdraw, create_task, list_tasks,
    get_task_by_id, mark_task_complete, initialize_tasks_table
)

TOKEN = '7316748216:AAFPxEeJ3nh7c16x46foda9EveyNFct-wko'
OWNER_ID = 5112568105  # Replace with your Telegram user ID

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    add_user(user.id, user.username)
    update.message.reply_text(
        f"Welcome to Earn $money Token Airdrop Bot, {user.first_name}!\n"
        "Use /airdrop to receive tokens, /balance to check your balance, "
        "/setaddress to set your withdrawal address, /refer to get your referral link, "
        "/dailybonus to claim your daily bonus, /withdraw to withdraw tokens, "
        "and /tasks to list available tasks."
    )

def airdrop(update: Update, context: CallbackContext):
    user = update.message.from_user
    add_user(user.id, user.username)
    update_balance(user.id, 10)  # Add 10 tokens for the airdrop
    update.message.reply_text("Airdrop successful! You received 10 tokens.")
    if context.args:
        referrer_id = int(context.args[0])
        if referrer_id != user.id and not is_referred(referrer_id, user.id):
            add_referral(referrer_id, user.id)
            update_balance(referrer_id, 5)  # Give referrer a bonus
            update.message.reply_text(
                f"Referrer bonus: {context.bot.get_chat(referrer_id).username} received 5 tokens."
            )

def balance(update: Update, context: CallbackContext):
    user = update.message.from_user
    balance = get_balance(user.id)
    update.message.reply_text(
        f"Your current balance is: {balance} $money tokens."
    )

def setaddress(update: Update, context: CallbackContext):
    user = update.message.from_user
    if context.args:
        address = context.args[0]
        set_withdrawal_address(user.id, address)
        update.message.reply_text(
            f"Withdrawal address set to: {address}"
        )
    else:
        update.message.reply_text(
            "Please provide an address using the command: /setaddress <your_address>"
        )

def refer(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text(
        f"Share this referral link: https://t.me/yourbotname?start={user.id}"
    )

def dailybonus(update: Update, context: CallbackContext):
    user = update.message.from_user
    if claim_daily_bonus(user.id):
        update.message.reply_text(
            "Daily bonus claimed! You received 10 $money tokens."
        )
    else:
        update.message.reply_text(
            "You have already claimed your daily bonus today."
        )

def withdraw(update: Update, context: CallbackContext):
    user = update.message.from_user
    if context.args:
        try:
            amount = float(context.args[0])
        except ValueError:
            update.message.reply_text(
                "Invalid amount. Please enter a valid number."
            )
            return

        result = withdraw(user.id, amount)
        if result == "Amount below minimum withdrawal limit.":
            update.message.reply_text(
                "The minimum withdrawal amount is 10,000 tokens. Please enter a higher amount."
            )
        elif result:
            update.message.reply_text(
                f"Withdrawal successful! Tokens sent to {result}."
            )
        else:
            update.message.reply_text(
                "Insufficient balance or no withdrawal address set."
            )
    else:
        update.message.reply_text(
            "Please specify the amount to withdraw using the command: /withdraw <amount>"
        )

def tasks(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.id == OWNER_ID:
        tasks_list = list_tasks(OWNER_ID)
        if tasks_list:
            response = "Available tasks:\n"
            for task in tasks_list:
                task_id, title, description, reward = task
                response += f"ID: {task_id}\nTitle: {title}\nDescription: {description}\nReward: {reward} $money tokens\n\n"
            update.message.reply_text(response)
        else:
            update.message.reply_text("No tasks available.")
    else:
        update.message.reply_text("You do not have permission to view tasks.")

def complete_task(update: Update, context: CallbackContext):
    user = update.message.from_user
    if context.args:
        try:
            task_id = int(context.args[0])
        except ValueError:
            update.message.reply_text("Invalid task ID. Please enter a valid number.")
            return
        task_info = get_task_by_id(task_id)
        if task_info:
            mark_task_complete(user.id, task_id)
            update.message.reply_text(f"Task '{task_info[0]}' completed! You received {task_info[2]} $money tokens.")
        else:
            update.message.reply_text("Task not found.")
    else:
        update.message.reply_text("Usage: /complete_task <task_id>")

def main():
    # Initialize the tasks table if it doesn't exist
    initialize_tasks_table()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("airdrop", airdrop))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("setaddress", setaddress))
    dp.add_handler(CommandHandler("refer", refer))
    dp.add_handler(CommandHandler("dailybonus", dailybonus))
    dp.add_handler(CommandHandler("withdraw", withdraw))
    dp.add_handler(CommandHandler("tasks", tasks))
    dp.add_handler(CommandHandler("complete_task", complete_task))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()