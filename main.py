import tweepy
import time
from binance.client import Client
import datetime
import json
from binance.exceptions import *

# Load Binance keys from json
binanceKeys = json.load(open('API/binance.json'))
binanceAPIKey = binanceKeys[0]
binanceAPISecret = binanceKeys[1]

# Create Binance client using parsed keys
client = Client(binanceAPIKey, binanceAPISecret)

# Variable strings for the composition
votesTweet = ""
priceTweet = ""
symbolTweet = ""
currentBalTweet = ""
startingBalTweet = 30.00  # <--float type (USD-T)
profitTweet = ""

sideTweet = ""
boughtTweet = ""

roundSeconds = 3600  # <--float type (Seconds in a 'round', defines how long the bot sleeps for)


# Help with adding/editing files
def append_new_line(file_name, text_to_append):
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)


# Set the client data for the Tweepy API (Partial scope with return)
def create_api():

    # Load Twitter Developer API keys from json
    twitterKeys = json.load(open('API/twitter.json'))

    print("\nInitializing Twitter Client ... create_api()")
    # Set OAuthHandler Keys
    consumer_key = twitterKeys[0]
    consumer_secret = twitterKeys[1]

    # Set Access Tokens
    access_token = twitterKeys[2]
    access_token_secret = twitterKeys[3]

    # Authenticate to twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Create API Object
    api = tweepy.API(auth)

    print("\nInitialized ... create_api() ... " + str(api))

    # Return the API as an object to the outer scope
    return api

# Check if a
def list_contains(List1, List2):
    check = False
    index = 0

    # Iterate in the 1st list
    for m in List1:

        # Iterate in the 2nd list
        for n in List2:

            # Track the index of the coinlist and return it

            # if there is a match
            if m == n:
                index = List2.index(n)
                check = True
                return check, index

    return check, index  # boolean


# Retrieve data from the Tweepy API using the client data in create_api()
def get_tweets(api):
    print("\nRunning Mention Filter ... get_tweets()")

    # Open the last mentioned tweet ID as the starting point for the round
    with open('logging/lastID.txt', 'r') as f:
        new_sid = f.read()
        f.close()

    print("\nRetrieving mentions since tweed ID #" + str(new_sid))

    # Clear the symbols from the previous round for an accurate count of the current round
    with open('logging/symbol.txt', 'w') as f:
        f.write("")
        f.close()

    print("\nRetrieving Mentions ... get_tweets() -> Tweepy API")

    # Get all mentions since the last checked ID
    tweets = api.mentions_timeline(since_id=new_sid)

    # Initialize needed values
    buyCount = 0  # Number of "Buy" votes for the current round, simple counter
    sellCount = 0  # Number of "Sell" votes for the current round, simple counter

    # If you wanted to save tweets, begin creating files here, and dump them to the `tweets/` folder

    print("\nMentions Retrieved ...\n\nProcessing Mentions ...")
    bSymbol = "-1"

    # Get the list of accepted symbols, and put each line into a list with the newline removed.
    acceptedCoins = [x[:-1] for x in open('logging/coinlist.txt', 'r').readlines()]
    print("Allowed coin list ... " + str(acceptedCoins))

    # Iterate through all tweets and check them for relevant information, save the info for later
    for t in tweets:

        # Print information about the current tweet
        print("\nScanned Tweet ID: " + str(t.id))
        print("\nScanned Tweet Text: " + str(t.text))

        # Get the fetched tweet as a list of strings, split it at the spaces, and change it to uppercase:
        fetchedTweet = t.text.upper().split(" ")
        print("Fetched Tweet -> " + str(fetchedTweet))

        hasCoin, coinIndex = list_contains(fetchedTweet, acceptedCoins)
        print("hasCoin = " + str(hasCoin) + "\ncoinIndex = "+ str(coinIndex))

        # If the hashtags for buy exist in the current tweet, do this
        if "#BUY" in fetchedTweet:

            # Add one to the total votes for "buy"
            buyCount = buyCount + 1
            print("\nScanned tweet contained a buy vote ... ")

            # Check for a trading pair/symbol in the current tweet, and if one exists, add it to "symbols.txt"

            if hasCoin:

                # Format the input text to set the symbol as the 3rd word in the tweet, and chop off any newlines,
                # spaces, or unwanted text
                bSymbol = str(acceptedCoins[coinIndex] + "USDT")

                # Do another check to make sure the symbol is JUST the desired coin, 1-5 chars + 4 chars for 'usdt'
                if 1 < len(bSymbol) <= 9:

                    # Save the current symbol to a new line on 'symbol.txt' without overwriting (append mode)
                    append_new_line("logging/symbol.txt", bSymbol)

                # If it's not in the correct format, don't add it to the list
                else:
                    print("The symbol didn't fit the format, so it wasn't added to the list ... " + str(bSymbol))

                # Print the symbol for confirmation
                print("\nScanned tweet contained a symbol ... " + bSymbol)

            # Otherwise, if the tweet didn't include a symbol, do nothing and print to the console
            else:
                print("Did nothing, we couldn't find a symbol here ...")

        # Otherwise, if the hashtags for sell exist in the current tweet, do this instead
        elif "#SELL" in fetchedTweet:

            # Add one to the total votes for "sell"
            sellCount = sellCount + 1
            print("\nScanned tweet contained a sell vote ... ")

            # Check for a trading pair/symbol in the current tweet, and if one exists, add it to "symbols.txt"
            if hasCoin:

                # Format the input text to set the symbol as the 3rd word in the tweet, and chop off any newlines,
                # spaces, or unwanted text
                bSymbol = str(acceptedCoins[coinIndex] + "USDT")

                # Do another check to make sure the symbol is JUST the desired coin, 1-5 chars + 4 chars for 'usdt'
                if 1 < len(bSymbol) <= 9:

                    # Save the current symbol to a new line on 'symbol.txt' without overwriting (append mode)
                    append_new_line("logging/symbol.txt", bSymbol)

                # If it's not in the correct format, don't add it to the list
                else:
                    print("The symbol didn't fit the format, so it wasn't added to the list ... " + str(bSymbol))

                # Print the symbol for confirmation
                print("\nScanned tweet contained a symbol ... " + bSymbol)

            # Otherwise, if the tweet didn't include a symbol, do nothing and print to the console
            else:
                print("Did nothing, we couldn't find a symbol here ...")

        # Check if the mention included a symbol without a #buy or #sell
        elif hasCoin and "#BUY" not in fetchedTweet and "#SELL" not in fetchedTweet:

            # Set the symbol to the selected coin + USDT
            bSymbol = str(acceptedCoins[coinIndex] + "USDT")

            # Do another check to make sure the symbol is JUST the desired coin, 1-5 chars + 4 chars for 'usdt'
            if 1 < len(bSymbol) <= 9:

                # Save the current symbol to a new line on 'symbol.txt' without overwriting (append mode)
                append_new_line("logging/symbol.txt", bSymbol)

            # If it's not in the correct format, don't add it to the list
            else:
                print("The symbol didn't fit the format, so it wasn't added to the list ... " + str(bSymbol))

            # Print the symbol for confirmation
            print("\nScanned tweet contained a symbol ... " + bSymbol)

        # If there is no symbol or vote, discard the tweet and don't count it.
        else:
            print("\nScanned tweet contained no vote ... ")

        # Save every tweet's ID to 'lastID.txt' in write mode. This will overwrite every non-last ID, leaving us the
        # ID of the most recently scanned mention. The bot will scan all mentions since the last voting period in the
        # next round, using this ID as the starting point.

        with open('logging/lastID.txt', 'w') as f:
            f.write(str(t.id))
            f.close()

    # Next, calculate if there were more buy or sell votes, and return a value 0-2 as 'isLong' so the bot knows what
    # action to take with the parsed information.
    if bSymbol == "-1":
        isLong = 0  # Do nothing, no symbols were given
        print("\nNo symbol provided ... doing nothing ...")

    elif buyCount < sellCount and bSymbol != "-1":
        isLong = 1  # SELL BTC
        print("\nSells beat buys, going short ...")

    elif sellCount < buyCount and bSymbol != "-1":

        print("\nBuys beat sells, going long ...")
        isLong = 2  # BUY BTC

    elif buyCount == sellCount and bSymbol != "-1":

        print("\nBuys equal sells, doing nothing ...")
        isLong = 0  # do nothing

    else:

        print("\nBuys and sells were not correctly returned ... get_tweets() -> else statement")
        isLong = 0  # do nothing

    return isLong, buyCount, sellCount


# Used to open an initial order
def create_order(symbolparam, quantityparam, sidestr):
    # Set leverage for selected symbol to 10x
    try:
        levSetting = client.futures_change_leverage(
            symbol=symbolparam,
            leverage=10
        )
    # If something goes wrong, try doing this
    except BinanceAPIException:
        print("\nError Setting Leverage! Log Below:\n\n" + str(BinanceAPIException))
        levSetting = ""

    print("\nLeverage set ... " + str(levSetting))

    # Use client.create_test_order() with same formatting to place a paper trade
    try:
        order = client.futures_create_order(
            symbol=symbolparam.replace("\n", "").upper(),
            side=sidestr,
            type="MARKET",
            quantity=float(quantityparam)
        )
    except BinanceAPIException:
        print("Create order exception triggered ... create_order -> except BinanceAPIException ... " + str(
            BinanceAPIException))
        order = -1

    # An order result of -1 suggests failure, while a returned dictionary is good
    print("\nOpen order returned ... " + str(order))

    return order


# Used to close the order after the round ends
def close_open_order(symbolparam, qtyparam, inversepos):
    try:
        order = client.futures_create_order(
            symbol=symbolparam.replace("\n", "").upper(),
            side=inversepos,
            type="MARKET",
            quantity=qtyparam
        )
        print("\nClose position function returned (working) ... " + str(order))
    except BinanceAPIException:
        print("\nError closing open position! Log Below:\n\n" + str(BinanceAPIException))


# Used to format the tweet sent out for each round
def compose_tweet(votes, price, symbol, balance, side, amount, profit):
    # Write to currentLog
    with open('logging/currentLog.txt', 'w') as f:
        f.write(
            "Stats | " + str(datetime.datetime.now())[0:20] + "\n\n" +
            "Votes: " + str(votes) + "\n" +
            "Side: " + str(side) + "\n" +
            "Pair: " + str(symbol) + "\n" +
            "Price: " + str(price) + "\n" +
            "Amount: " + str(amount) + "\n\n" +
            "Balance: " + str(balance) + "\n" +
            "Profit: " + str(profit) + "\n"
        )
        f.close()

    # Write to log
    with open('log.txt', 'a') as f:
        f.write(
            "Stats | " + str(datetime.datetime.now())[0:20] + "\n\n" +
            "Votes: " + str(votes) + "\n" +
            "Side: " + str(side) + "\n" +
            "Pair: " + str(symbol) + "\n" +
            "Price: " + str(price) + "\n" +
            "Amount: " + str(amount) + "\n\n" +
            "Balance: " + str(balance) + "\n" +
            "Profit: " + str(profit) + "\n"
        )
        f.close()

    tweet = ("Stats | " + str(datetime.datetime.now())[0:16] + "\n\n" +
             "Votes: " + str(votes) + "\n" +
             "Side: " + str(side) + "\n" +
             "Pair: " + str(symbol) + "\n" +
             "Price: " + str(price) + "\n" +
             "Amount: " + str(amount) + "\n\n" +
             "Balance: " + str(balance)[0:6] + "\n" +
             "Profit: " + str(profit)[0:6] + "\n")

    return tweet


# Main function
def main():
    # Create a Tweepy connection using the configurations
    tapi = create_api()

    # Infinite loop allows the script to run indefinitely, time.sleep() func handles hibernation between rounds for
    # accurate timing. Close the script or ctrl+x to exit.
    while True:

        # Fetch our mentions using Tweepy, and store the returned 'isLong' to 'long' for reference.
        long, longvotes, shortvotes = get_tweets(tapi)

        # If no votes were cast, or votes were equal, do nothing and update the results in currentLog.txt
        # DONE
        if long == 0:
            print("Did nothing!")

            priceTweet = "NA"
            sideTweet = "No Position"
            votesTweet = str(longvotes + shortvotes) + " | +" + str(longvotes) + " | -" + str(shortvotes)
            boughtTweet = "0"
            symbolTweet = "NA"
            currentBalTweet = float(
                [sub['balance'] for sub in client.futures_account_balance()][0])
            profitTweet = str(currentBalTweet - startingBalTweet)

            finalTweet = compose_tweet(votesTweet, priceTweet, symbolTweet, currentBalTweet, sideTweet, boughtTweet,
                                       profitTweet)

            # Send the tweet N/A!
            print(finalTweet)
            api = create_api()
            api.update_status(finalTweet)
            api.update_profile_image("img/Neutral.png")

            # sleep until the round ends then close the order and restart
            time.sleep(roundSeconds)

        # Otherwise, if our votes show short, do this
        elif long == 1:

            # Open Symbols file in read mode and find the most voted for symbol
            with open('logging/symbol.txt', 'r') as f:
                lines = f.readlines()
                print("\nPrinting 'symbol.txt' cache ... " + str(lines))
                frequent_word = ""
                frequency = 0
                words = []

                # Find the most frequent word
                for i in range(0, len(lines)):

                    # Declaring count
                    count = 1

                    # Count each word in the file
                    for j in range(i + 1, len(words)):
                        if lines[i] == lines[j]:
                            print(lines[i])
                            count = count + 1

                    # If the count value is more
                    # than highest frequency then
                    if count >= frequency:
                        frequency = count
                        frequent_word = lines[i]
                    else:
                        print("Count was not >= frequency ... main() -> elif long == 1 -> frequency counter")

                # Print results to the console
                print("\nHighest voted trading pair ... " + str(frequent_word))
                print("\nVotes for the above pair ... " + str(frequency))

                # Set the trading symbol to the most voted for coin, append "USDT", then transform the string to
                # uppercase.
                tSymbol = str(frequent_word).upper()

                # Close 'symbols.txt'
                f.close()

            # CLEAR THE TEXT FILE FOR NEXT ROUND
            with open('logging/symbol.txt', 'w') as f:
                f.write("")
                f.close()

            # To manually override the voted trading symbol with your own, uncomment the line below and replace pair.
            # tSymbol = "BTCUSDT" #---- TESTVALUE
            print("\nRead trading pair as ... " + str(tSymbol))

            # Calculate the amount we can safely short using our account balance and symbol price
            # Start by getting the futures account balance and printing it to the console
            balanceSell = float(
                [sub['balance'] for sub in client.futures_account_balance()][
                    0]) * 10  # 0 is USDT # 1 is BNB # 2 is BTC *10 is for 10x lev

            # Set currentBalTweet
            currentBalTweet = balanceSell / 10

            print("\nBuying power (10x leverage) ... " + str(balanceSell))

            # Print balance to console
            print("\nRetrieved futures account balance ... (USD-T) $" + str(balanceSell / 10))

            # Next, retrieve the close price of the selected symbol
            close = float(client.futures_symbol_ticker(symbol=tSymbol)['price'])

            # Set priceTweet
            priceTweet = str(close)

            # Print price to console
            print("\nRetrieved mark price of " + str(tSymbol) + " ... " + str(close))

            # Do some checks...
            # Get the min notional:
            minNotional = float(client.get_symbol_info(tSymbol)['filters'][2]['minQty'])
            print("\nSet smallest notional amount for (" + str(tSymbol) + ") ... " + str(minNotional))

            # Find max sell based on hardcoded percentages

            # balanceSell where 200 is 20 balance * 10x leverage (TESTVALUE)
            # FIX NOTIONAL CALCULATION HERE ------------v

            # notional finds the index of "." and starts the string there, omitting "0." in "0.001" leaving us "001"
            # Then, use the length of notional as the number of decimal places to round to in maxSell:
            notional = str(minNotional)
            if "." in notional:
                notional = str(notional)[str(notional).find("."):]
                # Sets notional = the number of decimal places
                notional = len(notional.replace(".", "")) - 1
            elif "e" in notional:
                notional = int(notional[3:]) - 1
                while notional >= 3:
                    notional = notional - 1
                while notional <= 1:
                    notional = notional + 1
                # Sets notional = the number of decimal places

            print("\nSet number of decimal places to round to ... " + str(notional))
            maxSell = float(balanceSell / close * 0.995)
            maxSell = round(maxSell, notional)  # 0.995 is percent balance

            # maxSell is the maximum allowable sell amount expressed in the traded currency (ex. BTC, not USD)
            print("\nMaximum sell order for (" + str(tSymbol) + ") ... " + str(maxSell))
            print("\nFormatted notional variable is ... " + str(notional))
            # format1 = "%." + str(len(notional)) + "f" %
            # print("Format is: " + format1)

            sQuantity = str(str("%." + str(notional) + "f") % float(maxSell * 0.15))  # 15% max sell

            print("The sQuantity is: " + str(sQuantity))

            # Ensure the quantity we're trying to get is greater than the notional, if it isn't draft a "failed" tweet
            if (len(sQuantity) - 1) < minNotional or float(sQuantity) < minNotional:
                print("The quantity was below the notional of " + str(minNotional) + "\n\n!!!\n")
                priceTweet = "0"
                sideTweet = "Failed Short"
                boughtTweet = "Quantity Below Notional :("
                symbolTweet = tSymbol
                currentBalTweet = float(
                    [sub['balance'] for sub in client.futures_account_balance()][0])
                profitTweet = str(currentBalTweet - startingBalTweet)
                votesTweet = str(longvotes + shortvotes) + " | +" + str(longvotes) + " | -" + str(shortvotes)

                finalTweet = compose_tweet(votesTweet, priceTweet, symbolTweet, currentBalTweet, sideTweet, boughtTweet,
                                           profitTweet)
                print(finalTweet)
                api = create_api()
                api.update_status(finalTweet)
                api.update_profile_image("img/Neutral.png")

                # Sleep until the round ends then restart (no close order required)
                time.sleep(roundSeconds)

            elif (len(sQuantity) - 1) >= minNotional and float(sQuantity) > 0:
                side = "SELL"
                order = create_order(tSymbol, sQuantity, side)

                profitTweet = str(currentBalTweet - startingBalTweet)
                votesTweet = str(longvotes + shortvotes) + " | +" + str(longvotes) + " | -" + str(shortvotes)
                currentBalTweet = float(
                    [sub['balance'] for sub in client.futures_account_balance()][0])
                sideTweet = "Short"

                # Swap out the params for appropriate values recieved from binance order response
                finalTweet = compose_tweet(votes=votesTweet, price=priceTweet, symbol=tSymbol, balance=currentBalTweet,
                                           side=sideTweet, amount=str(sQuantity), profit=profitTweet)

                # Send the tweet short!
                print(finalTweet)
                api = create_api()
                api.update_status(finalTweet)
                api.update_profile_image("img/Short.png")

                # sleep until the round ends then close the order and restart
                time.sleep(roundSeconds)
                inversePos = "BUY"
                close_open_order(tSymbol, sQuantity, inversePos)

            print("\nSell Round Complete ... ")

        # Otherwise, if our votes say long, do this
        elif long == 2:

            # Open Symbols file in read mode and find the most voted for symbol
            with open('logging/symbol.txt', 'r') as f:
                lines = f.readlines()
                print("\nPrinting 'symbol.txt' cache ... " + str(lines))
                frequent_word = ""
                frequency = 0
                words = []

                # Find the most frequent word
                for i in range(0, len(lines)):

                    # Declaring count
                    count = 1

                    # Count each word in the file
                    for j in range(i + 1, len(words)):
                        if lines[i] == lines[j]:
                            print(lines[i])
                            count = count + 1

                    # If the count value is more
                    # than highest frequency then
                    if count >= frequency:
                        frequency = count
                        frequent_word = lines[i]
                    else:
                        print("Count was not >= frequency ... main() -> elif long == 1 -> frequency counter")

                # Print results to the console
                print("\nHighest voted trading pair ... " + str(frequent_word))
                print("\nVotes for the above pair ... " + str(frequency))

                # Set the trading symbol to the most voted for coin, append "USDT", then transform the string to
                # uppercase.
                tSymbol = str(frequent_word).upper()

                # Close 'symbols.txt'
                f.close()

            # CLEAR THE TEXT FILE FOR NEXT ROUND
            with open('logging/symbol.txt', 'w') as f:
                f.write("")
                f.close()

            # To manually override the voted trading symbol with your own, uncomment the line below and replace pair.
            # tSymbol = "BTCUSDT" #---- TESTVALUE
            print("\nRead trading pair as ... " + str(tSymbol))

            # Calculate the amount we can safely short using our account balance and symbol price
            # Start by getting the futures account balance and printing it to the console
            balanceBuy = float(
                [sub['balance'] for sub in client.futures_account_balance()][
                    0]) * 10  # 0 is USDT # 1 is BNB # 2 is BTC *10 is for 10x lev

            # Set currentBalTweet
            currentBalTweet = balanceBuy / 10

            print("\nBuying power (10x leverage) ... " + str(balanceBuy))

            # Print balance to console
            print("\nRetrieved futures account balance ... (USD-T) $" + str(balanceBuy / 10))

            # Next, retrieve the close price of the selected symbol
            close = float(client.futures_symbol_ticker(symbol=tSymbol)['price'])

            # Set priceTweet
            priceTweet = str(close)

            # Print price to console
            print("\nRetrieved mark price of " + str(tSymbol) + " ... " + str(close))

            # Do some checks...
            # Get the min notional:
            minNotional = float(client.get_symbol_info(tSymbol)['filters'][2]['minQty'])
            print("\nSet smallest notional amount for (" + str(tSymbol) + ") ... " + str(minNotional))

            # Find max buy based on hardcoded percentages

            # balanceBuy where 200 is 20 balance * 10x leverage (TESTVALUE)
            # FIX NOTIONAL CALCULATION HERE ------------v

            # notional finds the index of "." and starts the string there, omitting "0." in "0.001" leaving us "001"
            # Then, use the length of notional as the number of decimal places to round to in maxSell:
            notional = str(minNotional)
            if "." in notional:
                notional = str(notional)[str(notional).find("."):]
                # Sets notional = the number of decimal places
                notional = len(notional.replace(".", "")) - 1
            elif "e" in notional:
                notional = int(notional[3:]) - 1
                while notional >= 3:
                    notional = notional - 1
                while notional <= 1:
                    notional = notional + 1
                # Sets notional = the number of decimal places

            print("\nSet number of decimal places to round to ... " + str(notional))
            maxBuy = float(balanceBuy / close * 0.995)
            maxBuy = round(maxBuy, notional)  # 0.995 is percent balance

            # maxBuy is the maximum allowable sell amount expressed in the traded currency (ex. BTC, not USD)
            print("\nMaximum buy order for (" + str(tSymbol) + ") ... " + str(maxBuy))
            print("\nFormatted notional variable is ... " + str(notional))
            # format1 = "%." + str(len(notional)) + "f"
            bQuantity = str(str("%." + str(notional) + "f") % float(maxBuy * 0.15))  # 15% max sell

            print("The bQuantity is ... " + str(bQuantity))

            # Ensure the quantity we're trying to get is greater than the notional, if it isn't draft a "failed" tweet
            if (len(bQuantity) - 1) < minNotional or float(bQuantity) < minNotional:
                print("The quantity was below the notional ... minNotional = " + str(minNotional) + "\n\n!!!\n")
                priceTweet = "0"
                sideTweet = "Failed Long"
                boughtTweet = "Quantity Below Notional :("
                symbolTweet = tSymbol
                currentBalTweet = float(
                    [sub['balance'] for sub in client.futures_account_balance()][0])
                profitTweet = str(currentBalTweet - startingBalTweet)
                votesTweet = str(longvotes + shortvotes) + " | +" + str(longvotes) + " | -" + str(shortvotes)

                finalTweet = compose_tweet(votesTweet, priceTweet, symbolTweet, currentBalTweet, sideTweet, boughtTweet,
                                           profitTweet)
                print(finalTweet)
                api = create_api()
                api.update_status(finalTweet)
                api.update_profile_image("img/Neutral.png")

                # Sleep until the round ends then restart (no close order required)
                time.sleep(roundSeconds)

            elif (len(bQuantity) - 1) >= minNotional and float(bQuantity) > 0:
                side = "BUY"
                order = create_order(tSymbol, bQuantity, side)

                profitTweet = str(currentBalTweet - startingBalTweet)
                votesTweet = str(longvotes + shortvotes) + " | +" + str(longvotes) + " | -" + str(shortvotes)
                currentBalTweet = float(
                    [sub['balance'] for sub in client.futures_account_balance()][0])
                sideTweet = "Long"

                # Swap out the params for appropriate values recieved from binance order response
                finalTweet = compose_tweet(votes=votesTweet, price=priceTweet, symbol=tSymbol, balance=currentBalTweet,
                                           side=sideTweet, amount=str(bQuantity), profit=profitTweet)

                # Send the tweet short!
                print(finalTweet)
                api = create_api()
                api.update_status(finalTweet)
                api.update_profile_image("img/Long.png")
                print("\nORDER PLACED || TWEET SENT || PROFILE UPDATED\n"
                      "_________________________________________________\n"
                      "Sleeping until the round finishes...")

                # sleep until the round ends then close the order and restart
                time.sleep(roundSeconds)
                inversePos = "SELL"
                close_open_order(tSymbol, bQuantity, inversePos)

            print("\nBuy Round Complete ... ")


if __name__ == '__main__':
    main()
