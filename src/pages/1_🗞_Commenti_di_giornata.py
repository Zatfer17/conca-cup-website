import streamlit as st
import requests
import pandas as pd

from bs4 import BeautifulSoup

def compute_old_leaderboard(leaderboard, latest_results):
    old_leaderboard = leaderboard.merge(latest_results, on='Squadra')
    old_leaderboard['Punti'] = old_leaderboard['Punti_x'] - old_leaderboard['Punti_y']
    old_leaderboard = old_leaderboard.sort_values(by='Punti', ascending=False).reset_index()[['index', 'Squadra', 'Punti']]
    old_leaderboard['Posizione'] = old_leaderboard['index'] + 1
    return old_leaderboard[['Posizione', 'Squadra', 'Punti']]

st.set_page_config(
    page_title='Conca Future Cup',
    page_icon='🗞',
    layout='wide'
)

st.title('🗞 Genera i commenti per la giornata corrente')

# Retrieve page id
r = requests.get('https://leghe.fantacalcio.it/conca-cup-tr/')
soup = BeautifulSoup(r.content, 'html.parser')
choices = soup.find_all('li', attrs={'class': 'dropdown-item'})

col1, col2 = st.columns(2)
with col1:
    division = st.selectbox('Per quale divisione vuoi generare i commenti?', ('A', 'B', 'C', 'D', 'E'))
with col2:
    competition = st.selectbox('Per quale competizione vuoi generare i commenti?', ('Campionato', 'Coppa Italia'))

if division and competition:
    for choice in choices:
        if ('-' in choice.text) & (choice.text.split(' - ')[0]==division) & (competition.lower() in choice.text.lower()):
            page_id = choice.find(attrs={"data-id": True})['data-id']
            break

# Display stats
col1, col2, col3 = st.columns(3)
r = requests.get(f'https://leghe.fantacalcio.it/conca-cup-tr/?id={page_id}')
soup = BeautifulSoup(r.content, 'html.parser')
# Latest leaderboard
leaderboard_data = []
rows = soup.find_all('tr', attrs={'class': 'ranking-row'})
for row in rows:
    columns = row.find_all('td')
    if competition == 'Campionato':
        leaderboard_data.append((int(columns[0].text), columns[2].text.replace('0', ''), float(columns[11].text.replace(',', '.'))))
    else:
        leaderboard_data.append((int(columns[0].text), columns[2].text.replace('0', ''), float(columns[10].text.replace(',', '.'))))
leaderboard = pd.DataFrame(leaderboard_data, columns=['Posizione', 'Squadra', 'Punti']).sort_values(by='Punti', ascending=False)
with col1:
    st.markdown('##### Classifica corrente')
    st.dataframe(leaderboard, hide_index=True)
# Latest results
latest_results_data = []
rows = soup.find_all('li', attrs={'class': 'list-group-item match match-result row highlight'}) 
if competition == 'Campionato':
    for row in rows:
        latest_results_data.append((row.find('h5', attrs={'class': 'team-name'}).text, float(row.find('div', attrs={'class': 'team-fpt'}).text.replace(',', '.'))))
    latest_results = pd.DataFrame(latest_results_data, columns=['Squadra', 'Punti']).sort_values(by='Punti', ascending=False)
else:
    for row in rows:
        home = row.find('div', attrs={'class': 'team-home col-xs-6'})
        away = row.find('div', attrs={'class': 'team-away col-xs-6'})
        home_team = home.find('h5', attrs={'class': 'team-name'}).text
        home_goals = int(home.find('div', attrs={'class': 'team-score'}).text)
        away_team = away.find('h5', attrs={'class': 'team-name'}).text
        away_goals = int(away.find('div', attrs={'class': 'team-score'}).text)
        if home_goals > away_goals:
            home_points = 3
            away_points = 0
        elif home_goals < away_goals:
            home_points = 0
            away_points = 3
        else:
            home_points = 1
            away_points = 1
        latest_results_data.append((home_team, home_points, f'{home_goals} - {away_goals}', away_team))
        latest_results_data.append((away_team, away_points, f'{away_goals} - {home_goals}', home_team))
    latest_results = pd.DataFrame(latest_results_data, columns=['Squadra', 'Punti', 'Risultato', 'Avversario'])
with col2:
    st.markdown('##### Ultimi risultati')
    st.dataframe(latest_results, hide_index=True)
# Previous leaderboard
old_leaderboard = compute_old_leaderboard(leaderboard, latest_results)
with col3:
    st.markdown('##### Classifica precedente')
    st.dataframe(old_leaderboard, hide_index=True)

st.markdown('##### Ora vai sul [sito di chatGPT](https://chat.openai.com/) (registrati se necessario) e incolla il messaggio di seguito per ottenere i commenti di giornata!')
if competition == 'Campionato':
    st.code(
    f'''
    Commenta l'ultima giornata di fantacalcio confrontando la classifica prima:

    {old_leaderboard.drop(columns=['Punti']).to_string(index=False)}

    e dopo:

    {leaderboard.drop(columns=['Punti']).to_string(index=False)}

    Per favore, indica in ordine:
    - quale squadra ha guadagnato posizioni in classifica;
    - quale squadra ha perso posizioni in classifica;
    - quali squadre sono nella metá superiore della classifica e non pagheranno (per ora) la cena di fine anno.

    Inoltre, sapendo che questi sono stati i risultati della giornata:

    {latest_results.to_string(index=False)}

    indica:
    - quale squadra ha totalizzato piú punti in assoluto;
    - quale squadra ha totalizzato meno punti in assoluto;

    Evidenzia in grassetto i nomi delle squadre, usa le emoji e ricordati di sottolineare il discorso della cena.
    '''
    )
else:
    st.code(
    f'''
    Commenta l'ultima giornata di fantacalcio confrontando la classifica prima:

    {old_leaderboard.drop(columns=['Punti']).to_string(index=False)}

    e dopo:

    {leaderboard.drop(columns=['Punti']).to_string(index=False)}

    Per favore, indica in ordine:
    - quale squadra ha guadagnato posizioni in classifica;
    - quale squadra ha perso posizioni in classifica;

    Inoltre, sapendo che questi sono stati i risultati della giornata:

    {latest_results.to_string(index=False)}

    indica:
    - quale squadra ha segnato piú gol in assoluto;
    - quale squadra ha vinto con piú gol di scarto;
    - quale é stata la partita con piú gol complessivi;

    Evidenzia in grassetto i nomi delle squadre e usa le emoji.
    '''
    )

