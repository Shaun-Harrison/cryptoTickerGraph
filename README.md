# cryptoTickerGraph

![Image Preview](https://github.com/Shaun-Harrison/cryptoTickerGraph/blob/main/eth_screenshot.jpg?raw=true)

Modified version of https://github.com/dr-mod/zero-btc-screen 

Follow all setup instructions in this repo before cloning this repo

Changes include 
-   Use coingecko to get price information - This API has more options than the previous
-   Multiple Tokens - see main.py line 21 & 34 to modify token list
-   Daily percentage - Added in the coins daily percentage change
-   Change to looping logic - This was so that the screen would loop through the different tokens & for if the API returns non 200 it doesn't exit the script
-   Minor changes - such as font / removal of lines / font sizes all to suit my needs / wants
