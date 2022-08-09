# Whatsapp Group Analyzer


Analyze automatically your WhatsApp group conversations just by uploading a text file. 
Go to the application [website](https://arnautt-whatsapp-group-analyzer-app-14gt3z.streamlitapp.com/),
follow the instructions on the sidebar and enjoy !



## Examples gallery

- Various information about the authors of the conversation showing,
for example, the podium of the most active or those who send the most media. 

<p align="center">
  <img src="assets/description_1.png" width="700" height="450"/>
</p>

<p align="center">
  <img src="assets/description_2.png" width="700" height="450"/>
</p>



- The most used words in the conversation by removing the stop words (i.e. common / useless words) : 
the size of the words is proportional to its frequency.

<p align="center">
  <img src="assets/wordcloud.png" width="700" height="450"/>
</p>



- The percentage of messages with an emoji for each participant in the conversation.

<p align="center">
  <img src="assets/emoji_usage.png" width="700" height="450"/>
</p>



- Interactive comparison of the sending times of each message.

<p align="center">
  <img src="assets/hour_comparison.png" width="700" height="450"/>
</p>


- Distribution of the most used emojis with analysis of the biggest contributors.

<p align="center">
  <img src="assets/emoji_percentages.png" width="500" height="450"/>
</p>


- And much more ! Use it with your own conversations to know them :)

## :warning: Remarks


1. The application allows you to analyze WhatsApp groups only.
So you have to choose a **conversation with at least 3 people**.

2. Depending on OS and language, WhatsApp conversation format can vary a lot.
There are currently two supported formats (one for French and one for English conversation). 
If you want the application to be compatible with your format, you can either :


- Add your WhatsApp format to the current code by adding it
[here](https://github.com/Arnautt/whatsapp-group-analyzer/blob/master/app.py#L32-L46) 

You'll need to specify two variables : **date_format** (Python datetime format of your conversation)
and **header** (the associated regex with the extra character between date and message name)

- Or format your conversation to one of the two known formats at the moment :

```
10/03/2022 à 19:49 - Name: Your message (French WhatsApp)
6/20/19, 19:49 - Name: Your message (English WhatsApp)
```

3. The application uses Natural Language Processing and a wordcloud plot to analyze the words of your conversation.
If your conversation is not in French or English, please add your language
[here](https://github.com/Arnautt/whatsapp-group-analyzer/blob/master/app.py#L78-L85), 
following the same structure.


## :rocket: Technical stack 

- Data Processing : pandas
- Data Visualization : pyplot, seaborn, plotly
- Application Deployment : streamlit 
- Natural Language Processing : nltk 

