import requests
import json
import tabula
import re
import streamlit as st

def get_substance(x):
    'Returns the substance of the drug.'
    l  = x.split('\r')
    s = re.search(r'\w+', l[-1]).group()
    return s.lower()

# Get the pdf with prescriptions from the user.

st.title('Medicinkollen 🕵️')
st.markdown('''
🧑‍⚕️ *Läkare ska ha koll på dina recept så att inga mediciner "krockar" men
ibland finns inte den tiden i sjukvården.*  
💊 *Det finns rapporter om att exempelvis äldre människor ibland har en lång 
lista med läkemedel där inte alla kombinationer är bra.*  
🧑‍💻 *Genom att logga in på [1177.se](https://1177.se)
och gå till läkemedelstjänster kan du ladda hem en PDF där det syns vilka
läkemedel du har.*  
🔎 *Den PDF\:en kan du sedan ladda upp här för att få information från 
[Janusmed](https://janusmed.se) - som drivs av bl.a. Region Stockholm – med eventuella
varningar.*  
😌 *Ingen information sparas i den här tjänsten.*
''')
pdf = st.file_uploader(label='Ladda upp din läkemedelslista', type='pdf')

if pdf:

    # Extract table from prescription pdf.
    area = [111, 20, 528, 822]
    df = tabula.read_pdf(pdf, pages='all', area=area, lattice=True)[0]
    df.columns = ['Uthämtat datum', 'Uthämtat läkemedel', 'Användning', 'Förskrivet av', 'Uthämtad mängd', 'Läkemedelsgrupp']
    df.dropna(axis=0, inplace=True)
    df['substance'] = df['Uthämtat läkemedel'].apply(lambda x: get_substance(x))

    # Make list of precripted substances.
    substances = df.substance.tolist()

    substances_id_list = []
    for substance in substances:
        # Get data for the substance.
        data = requests.get(f'https://janusmed.se/api/search/input/{substance}').json()
        data = data[0] # Only first is interesting(?) when searching on substances.

        # Add the substance ID to the list of substances.
        substance_id = data['nslId'] #TODO Kan finnas flera!?
        substances_id_list.append(substance_id)

    # Create URL for janusmed.se 
    substances_id_url_list = '&nslIds='.join(substances_id_list)
    url = 'https://janusmed.se/interaktioner?nplIds=' + substances_id_url_list
    
    # Show text with URL to janusmed.
    st.markdown(f'''
    :grey[*Följ [den här länken]({url}) för att se om dina 
    läkemedel går bra ihop eller om det kan finnas något
    du skulle kunna prata med din läkare om. Nedan kan du se en förhandsvisning.*]
    ''')

    # View janusmed.se in an iframe.
    st.components.v1.iframe(url, height=600, scrolling=True)

