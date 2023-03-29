import datetime
import calendar
import pandas as pd
import streamlit as st

meeting_places = ["Frohburg-/Letzistrasse", "Thiwa Cafe @ Triemli", "Oil! Tankstelle Fronwaldstrasse", "Fork & Bottle @ Sihlcity"]
st.title("ride generator for zürides.ch")
with st.form("Ride text generator"):
    d = st.date_input(
        "When\'s your ride",
        datetime.date.today())
    title = st.text_input("Enter the ride title: ")
    level = st.radio("enter the ride level: ", ("☕" , "🦵", "🔥"))
    avg = st.slider('Expected average?', 18, 35, 26)
    meeting_spot = st.multiselect("enter the meeting spot: ", meeting_places)
    desc = st.text_input("Enter a short description (tweet lenght): ")
    link = st.text_input("Add the link to the strava route: ")
    col1, col2 = st.columns(2)
    with col1:
        dist= st.number_input("Enter the distance in km",value = 100, step = 1)
    with col2:
        elev = st.number_input("Enter the positive elevation gain in m", value = 1000, step = 1)
    #stats = st.text_input("Add the stats in the format '100km, 100m' : ")
    name1 = st.text_input("Name of the first ride leader: ")
    name2 = st.text_input("Name of the second ride leader (leave blank if not appliable)")
    submitted = st.form_submit_button("Generate Template")

#print( d.day_name(), d.month_name())

try:
    meeting_spot[0]
    bigtext  = f"""
-- {d.strftime('%A')}, {d.day} {calendar.month_name[d.month]}  --

*Sign up here:*  https://registration.zürides.ch/
Select the ride you prefer, make sure you received the confirmation email, and please use the link in that email if you want to remove or change your registration. 

*{title}*
{name1}@..., {name2} @... 
*Route:* {int(dist)}km and {int(elev)}m of elevation gain,  {link}
*Ride level:* {level}, {avg-1}-{avg+1} km/h 
*Meeting time&place:*  at *{meeting_spot[0]}* 
{desc} We will ride together in a group at a brisk but comfortable pace on the flats. On the hills, you choose your speed and we regroup on the top. 

"""
    st.code(bigtext)

    if len(meeting_spot) != 1:
        st.warning("The wrong number of meeting places selected")
except IndexError:
    st.info("Press the submit button")



