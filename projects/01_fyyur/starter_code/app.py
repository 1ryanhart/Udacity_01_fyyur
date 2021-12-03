#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app.config.from_object('config')

migrate=Migrate(app, db)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

current_time = datetime.utcnow()

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data=[]
    venues=[]

    # returns a list of the City/State pairs
    places = Venue.query.distinct(Venue.state, Venue.city).all()

    for place in places:
        venues = Venue.query.filter(Venue.state==place.state, Venue.city==place.city)
        entry = {
            'city': place.city,
            'state': place.state,
            'venues': [] }
        for venue in venues:
            entry['venues'].append({
                    'id':venue.id,
                    'name':venue.name,
                    'num_upcoming_shows':Show.query.filter(Show.venue_id==venue.id, Show.start_time> current_time)
                    })
        data.append(entry)
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term=request.form.get('search_term', '')

  # returns a list venues based on case-insensitive partial string search
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  response={
    'count':len(venues),
    'data': []
    }

  for venue in venues:
    response['data'].append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows':Show.query.filter(Show.venue_id==venue.id, Show.start_time> current_time).count()})

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue=Venue.query.get(venue_id)
  data = {
     'id':venue.id,
     'name' : venue.name,
     'city' : venue.city,
     'state' : venue.state,
     'phone' : venue.phone,
     'genres' : venue.genres,
     'image_link' : venue.image_link,
     'facebook_link' : venue.facebook_link,
     'website' : venue.website,
     'seeking_talent' : venue.seeking_talent,
     'seeking_description' : venue.seeking_description,
     'upcoming_shows' : [],
     'past_shows' : [],
  }
  # shows = Show.query.filter(Show.venue_id==venue.id) // this was the code that was previously in for submission1

  shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue.id)

  for show in shows:
        if show.start_time> current_time:
           data['upcoming_shows'].append({
           'artist_image_link': Artist.query.filter(Artist.id==show.artist_id).first().image_link,
           'artist_name': Artist.query.filter(Artist.id==show.artist_id).first().name,
           'start_time':show.start_time.strftime("%d/%m/%Y, %H:%M")
           })
        else:
           data['past_shows'].append({
           'artist_image_link': Artist.query.filter(Artist.id==show.artist_id).first().image_link,
           'artist_name': Artist.query.filter(Artist.id==show.artist_id).first().name,
           'start_time':show.start_time.strftime("%d/%m/%Y, %H:%M")
           })
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  data['past_shows_count'] = len(data['past_shows'])
  # TODO: replace with real venue data from the venues table, using venue_id
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)
    try:
        venue = Venue(
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            address = form.address.data,
            phone = form.phone.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            website = form.website_link.data,
            seeking_talent = form.seeking_talent.data,
            seeking_description = form.seeking_description.data
            )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        return render_template('pages/home.html')
    else:
        return render_template('pages/home.html')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue deleted successfully')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Venue could not be deleted.')
  finally:
      db.session.close()
  return  redirect(url_for('venues'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  response={
    'count':len(artists),
    'data': []
    }

  for artist in artists:
    response['data'].append({
    'id':artist.id,
    'name':artist.name,
    'num_upcoming_shows':Show.query.filter(Show.artist_id==artist.id, Show.start_time> current_time).count()})

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=Artist.query.get(artist_id)
  data = {
    'id':artist.id,
    'name' : artist.name,
    'city' : artist.city,
    'state' : artist.state,
    'phone' : artist.phone,
    'genres' : artist.genres,
    'image_link' : artist.image_link,
    'facebook_link' : artist.facebook_link,
    'website' : artist.website,
    'seeking_venue' : artist.seeking_venue,
    'seeking_description' : artist.seeking_description,
    'upcoming_shows' : [],
    'past_shows' : [],
  }
  # shows = Show.query.filter(Show.artist_id==artist.id) // this was the code that was previously in for submission1
  shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist.id)
  
  for show in shows:
      if show.start_time> current_time:
          data['upcoming_shows'].append({
          'venue_image_link': Venue.query.filter(Venue.id==show.venue_id).first().image_link,
          'venue_name': Venue.query.filter(Venue.id==show.venue_id).first().name,
          'start_time':show.start_time.strftime("%d/%m/%Y, %H:%M")
          })
      else:
          data['past_shows'].append({
          'venue_image_link': Venue.query.filter(Venue.id==show.venue_id).first().image_link,
          'venue_name': Venue.query.filter(Venue.id==show.venue_id).first().name,
          'start_time':show.start_time.strftime("%d/%m/%Y, %H:%M")
          })
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  data['past_shows_count'] = len(data['past_shows'])
  return render_template('pages/show_artist.html', artist=data )


#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    form = ArtistForm(request.form)
    artist = Artist.query.get_or_404(artist_id)
    try:
        artist.name=form.name.data
        artist.genres=form.genres.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.website=form.website_link.data
        artist.facebook_link=form.facebook_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        artist.image_link=form.image_link.data
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully edited!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
        return render_template('pages/home.html')
    else:
  # TODO: take values from the form submitted, and update existing
        return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  venue= Venue.query.get_or_404(venue_id)
  try:
          venue.name=form.name.data
          venue.genres=form.genres.data
          venue.city=form.city.data
          venue.address=form.address.data
          venue.state=form.state.data
          venue.phone=form.phone.data
          venue.website=form.website_link.data
          venue.facebook_link=form.facebook_link.data
          venue.seeking_talent=form.seeking_talent.data
          venue.seeking_description=form.seeking_description.data
          venue.image_link=form.image_link.data
          db.session.commit()
          flash('Venue ' + form.name.data + ' was successfully edited!')
  except:
          error = True
          db.session.rollback()
  finally:
          db.session.close()
  if error:
          flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')
          return render_template('pages/home.html')
  else:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    error = False
    try:
        artist = Artist(
            name=form.name.data,
            genres=form.genres.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data,
            )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
        return render_template('pages/home.html')
    else:
        return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.all()
  for show in shows:
          data.append({"venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time":show.start_time.strftime("%d/%m/%Y, %H:%M")})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error = False
  try:
    show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data,
        )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  else:
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
