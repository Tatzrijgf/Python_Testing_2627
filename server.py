import pkgutil
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

booking_history = {club['name']: {} for club in clubs}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    # 1. On cherche tous les clubs correspondants
    matching_clubs = [club for club in clubs if club['email'] == request.form['email']]
    
    # 2. Si aucun club n'est trouvé, on affiche un message et on redirige vers l'accueil
    if not matching_clubs:
        flash("Cette adresse e-mail n'est pas enregistrée.", "error")
        return redirect(url_for('index'))
        
    # 3. Si un club existe, on prend le premier de la liste en toute sécurité
    club = matching_clubs[0]
    return render_template('welcome.html', club=club, competitions=competitions, today=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    # Recherche sécurisée du club
    matching_clubs = [c for c in clubs if c['name'] == club]
    # Recherche sécurisée de la compétition
    matching_competitions = [c for c in competitions if c['name'] == competition]
    
    # Si l'un des deux n'existe pas, on lève une sécurité
    if not matching_clubs or not matching_competitions:
        flash("Ressource introuvable. Veuillez réessayer.")
        return redirect(url_for('index'))
        
    foundClub = matching_clubs[0]
    foundCompetition = matching_competitions[0]
    
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    matching_competitions = [c for c in competitions if c['name'] == request.form['competition']]
    matching_clubs = [c for c in clubs if c['name'] == request.form['club']]
    
    if not matching_competitions or not matching_clubs:
        flash("Une erreur est survenue lors de la sélection des données.")
        return redirect(url_for('index'))
        
    competition = matching_competitions[0]
    club = matching_clubs[0]
    
    # Génération systématique de la date pour le rendu des erreurs
    current_date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    placesRequired = int(request.form['places'])

    if placesRequired <= 0:
        flash("Erreur : Le nombre de places demandées doit être supérieur à zéro.")
        return render_template('welcome.html', club=club, competitions=competitions, today=current_date_str)
    
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Erreur : Il ne reste que {competition['numberOfPlaces']} places disponibles.")
        return render_template('welcome.html', club=club, competitions=competitions, today=current_date_str)

    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < datetime.now():
        flash("Erreur : Impossible de réserver des places pour une compétition passée.")
        return render_template('welcome.html', club=club, competitions=competitions, today=current_date_str)

    already_booked = booking_history[club['name']].get(competition['name'], 0)

    if already_booked + placesRequired > 12:
        flash(f"Erreur : Vous ne pouvez pas réserver plus de 12 places au total. Déjà réservé : {already_booked}.")
        return render_template('welcome.html', club=club, competitions=competitions, today=current_date_str)

    if placesRequired > int(club['points']):
        flash("Erreur : Vous n'avez pas assez de points pour réserver ce nombre de places.")
        return render_template('welcome.html', club=club, competitions=competitions, today=current_date_str)
    
    # Application des changements
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = str(int(club['points']) - placesRequired)
    booking_history[club['name']][competition['name']] = already_booked + placesRequired
    
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions, today=current_date_str)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
