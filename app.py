#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from itertools import count
import json
from unittest import result
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
from operator import itemgetter
import collections
from models import db, Venue, Artist, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
     date = value
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

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = db.session.query(Venue).all()

    data = [] 

    city_state = set()
    for venue in venues:
        city_state.add( (venue.city, venue.state) )
    
    city_state = list(city_state)
    city_state.sort(key=itemgetter(1,0))     

    for loc in city_state:
        venues_list = []
        for venue in venues:
            if (venue.city == loc[0]) and (venue.state == loc[1]):
                  venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                })
        data.append({
            "city": loc[0],
            "state": loc[1],
            "venues": venues_list
        })

   
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  form = SearchForm(request.form)
  if form.validate_on_submit:
    search_term=request.form.get('search_term', '')
    venue_search=Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    data=[]
    for venue in venue_search:
      data.append({
        "id" : venue.id,
        "name" : venue.name,
    })
  
    response = {
      "count": len(venue_search),
      "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get("search_term", ""))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  current_time = datetime.now()
  if not venue:
    return redirect(url_for('index'))
  upcoming_query =(
    db.session.query(Shows)
    .join(Artist)
    .filter(Shows.venue_id == venue_id)
    .filter(Shows.start_time >= current_time)
    .all()
  )
  upcoming_shows = []
  past_query =(
  db.session.query(Shows)
  .join(Artist)
  .filter(Shows.venue_id == venue_id)
  .filter(Shows.start_time <= current_time)
  .all()
  )
  past_shows = []
 
  for show in past_query:
    past_shows.append({
      "artist_id" : show.artist.id,
      "artist_name" : show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
  for show in upcoming_query:  
    upcoming_shows.append({
      "artist_id" : show.artist.id,
      "artist_name" : show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
  data={
    "id": venue.id,
    "name": venue.name,
    "genres":venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form=VenueForm(request.form)
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data  
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

  # on successful db insert, flash success
    new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres = genres ,\
              seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
              website=website_link, facebook_link=facebook_link)
   
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('venues'))
  except:
        flash('Venue ' + request.form['name'] + '  could not be listed!')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.route('/venues/delete/<venue_id>', methods=['GET', 'POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue_to_delete = Venue.query.get(venue_id)

  try:
    db.session.delete(venue_to_delete)
    db.session.commit()
    flash("Venue was deleted")
    return redirect(url_for('home'))
  except:
    db.rollback()
    flash("Venue was not deleted")
  finally:
    db.session.close()
    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists=Artist.query.all()
  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  form = SearchForm(request.form)
  if form.validate_on_submit:
    search_term=request.form.get('search_term', '')
    artist_search=Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    data=[]
    for artist in artist_search:
      data.append({
        "id" : artist.id,
        "name" : artist.name
    })
    response = {
      "count": len(artist_search),
      "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get("search_term", ""))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=Artist.query.get(artist_id)
  current_time = datetime.now()
  if not artist:
    return redirect(url_for('index'))
  upcoming_query =(
    db.session.query(Shows)
    .join(Artist)
    .filter(Shows.artist_id == artist_id)
    .filter(Shows.start_time >= current_time)
    .all()
  )
  upcoming_shows = []
  past_query =(
  db.session.query(Shows)
  .join(Artist)
  .filter(Shows.artist_id == artist_id)
  .filter(Shows.start_time <= current_time)
  .all()
  )
  past_shows = []
 
  for show in past_query:
    past_shows.append({
      "venue_id" : show.venue.id,
      "venue_name" : show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
  for show in upcoming_query:  
    upcoming_shows.append({
      "venue_id" : show.venue.id,
      "venue_name" : show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
  data={
    "id": artist.id,
    "name": artist.name,
    "genres":artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_talent": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  if request.method == 'POST':

        
        return redirect(url_for('index'))
  else:
        form = ArtistForm(obj=artist)
 
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres":artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  if request.method == 'POST':
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    website = form.website_link.data
    facebook_link = form.facebook_link.data
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data
    image_link = form.image_link.data

    try:
      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.genres = genres
      artist.website = website
      artist.facebook_link=facebook_link
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      artist.image_link = image_link

      db.session.add(artist)
      db.session.commit()
      flash('Artist was successfully updated!')
      return redirect(url_for('show_artist', form = form ,artist_id=artist.id))
    except:
      flash('An error occurred. Artist could not be updated.')
      return redirect(url_for('show_artist', form = form ,artist_id=artist.id))
    finally:
      db.session.close()
  else:
    return redirect(url_for('show_artist', form = form ,artist_id=artist.id))
    

      # on successful db update, flash success

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  if request.method == 'POST':
    return redirect(url_for('index'))
  else:
    form = VenueForm(obj=venue)
  venue={
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state,
    "address" : venue.address,
    "genres":venue.genres,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  if request.method == 'POST':
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.phone.data
    genres = form.genres.data
    website = form.website_link.data
    facebook_link = form.facebook_link.data
    seeking_talent = True if form.seeking_talent.data == 'Yes' else False
    seeking_description = form.seeking_description.data
    image_link = form.image_link.data

    try:
      venue.name = name
      venue.city = city
      venue.state = state
      venue.address = address
      venue.genres = genres
      venue.website = website
      venue.facebook_link=facebook_link
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      venue.image_link = image_link

      db.session.add(venue)
      db.session.commit()
      flash('Venue was successfully updated!')
      return redirect(url_for('show_venue', form = form ,venue_id=venue.id))
    except:
      flash('An error occurred. Venue could not be updated.')
      return redirect(url_for('show_venue', form = form ,venue_id=venue.id))
    finally:
      db.session.close()
  else:
    return redirect(url_for('show_venue', form = form ,venue_id=venue.id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data   
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
  # on successful db insert, flash success
    new_artist=Artist(name=name, city=city, state=state, phone=phone,facebook_link=facebook_link, genres =genres, \
              image_link=image_link, website=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description,  \
               )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('artists')) 
  except:
    db.session.rollback
    flash('An error occurred. Artist could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/artists/delete/<artist_id>', methods=['GET', 'POST'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  artist_to_delete = Artist.query.get(artist_id)

  try:
    db.session.delete(artist_to_delete)
    db.session.commit()
    flash("Artist was deleted")
    return redirect(url_for('home'))
  except:
    db.session.rollback()
    return redirect(url_for('artists'))
  finally:
    db.session.close()
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Shows).join(Artist).join(Venue).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time,
  })
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
  form = ShowForm()

  artist_id = form.artist_id.data.strip()
  venue_id = form.venue_id.data.strip()
  start_time = form.start_time.data
    
  try:
    new_show = Shows(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash(f'An error occurred.  Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
