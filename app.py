#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.mime import image
from email.policy import default
import json
from types import CoroutineType
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link=db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description=db.Column(db.String(200))
    shows=db.relationship('Show',backref='Venue', lazy=True)
    date_created=db.Column(db.DateTime(), default=datetime.utcnow())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link=db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description=db.Column(db.String(200))
    shows=db.relationship('Show', backref='Artist', lazy=True)
    date_created=db.Column(db.DateTime(), default= datetime.utcnow())

  



class Show(db.Model):
  __tablename__='shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id=db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id=db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time=db.Column(db.DateTime(), nullable=False)


db.create_all()


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date=dateutil.parser.parse(value)
  else:
    date=value
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

@app.route("/venues")
def venues():
  data_areas= Venue.query.all()
  data = []
  for place in data_areas:
    venues = Venue.query.filter(Venue.city==place.city, Venue.state==place.state).all()

    data.append({
      "city":place.city,
      "state":place.state,
      'venues':venues
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  results = Venue.query.filter(Venue.name.ilike('%{}'.format(request.form['search_term']))).all()
  response ={
    "count":len(results),
    "data":[]
  }
  for venue in results:
    search_data= {
      "data":venue.id,
      "name":venue.name
    }
    response["data"].append(search_data)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

 

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter(Venue.id==venue_id).first()
  upcoming_shows =Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.start_time > datetime.now())
  past_shows = Show.query.join(Venue).filter(Artist.id == venue_id).filter(Show.start_time <= datetime.now())
  upcoming_shows_count=upcoming_shows.count()
  past_shows_count=past_shows.count()

  data = {
    "id":venue.id,
    "name":venue.name,
    "genres":venue.genres,
    "city":venue.city,
    "state":venue.state,
    "phone":venue.phone,
    "image_link":venue.image_link,
    "facebook_link":venue.facebook_link,
    "weebsite_link":venue.website_link,
    "seeking_talent":venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count":past_shows_count,
    "upcoming_shows_count":upcoming_shows_count


  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm
    name = request.form.get('name', '')
    city = request.form.get('city','')
    state = request.form.get('state', '')
    address=request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres =request.form.get('genres','')
    facebook_link=request.form.get('facebook_link', '')
    image_link=request.form.get('image_link', '')
    website_link=request.form.get('website_link', '')
    seeking_talent=request.form.get('seeking_talent')
    seeking_description=request.form.get('seeking_description','')

    todo = Venue(
     name=name,
     city=city, 
     state=state, 
     address=address,
     phone=phone,
     genres=genres,
     facebook_link=facebook_link,
     image_link=image_link,
     website_link=website_link,
     seeking_talent=seeking_talent,
     seeking_description=seeking_description
     
     )
    db.session.add(todo)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')


  except:
    flash('Venue ' + request.form['name'] + ' was not  successfully listed! Try again')
    db.session.rollback()
  finally:
     db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash("The Venue was deleted was successful")
  except:
    db.session.rollback()
    flash("The Venue was not deleted.Try again")
  finally:
    db.session.close()
  return redirect(url_for('index'))

  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

  

@app.route('/artists/search', methods=['POST'])
def search_artists():

    
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  results = Artist.query.filter(Artist.name.ilike('%{}'.format(request.form['search_term']))).all()
  response ={
    "count":len(results),
    "data":[]
  }
  for artist in results:
    search_data= {
      "data":artist.id,
      "name":artist.name
    }
    response["data"].append(search_data)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  upcoming_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.start_time > datetime.now())
  past_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.start_time <= datetime.now())
  past_shows_count = past_shows.count()
  upcoming_shows_count = upcoming_shows.count()

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "image_link":artist.image_link,
    "facebook_link": artist.facebook_link,
    "website_link":artist.website_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count":upcoming_shows_count
  }
  

  return render_template('pages/show_artist.html', artist=data)
      
  
  


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id==artist_id).first()
  forms = ArtistForm()
  forms.name.data=artist.name
  forms.city.data=artist.city
  forms.state.data=artist.state
  forms.phone.data=artist.phone
  forms.genres.data=artist.genres
  forms.image_link.data=artist.image_link
  forms.facebook_link.data=artist.facebook_link
  forms.website_link.data=artist.website_link
  forms.seeking_venue=artist.seeking_venue
  forms.seeking_description=artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=forms, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    name = request.form.get('name', '')
    city=request.form.get('city', '')
    state=request.form.get('state','')
    phone=request.form.get('phone', '')
    genres=request.form.get('genres','')
    image_link=request.form.get('image_link','')
    facebook_link=request.form.get('facebook_link','')
    website_link=request.form.get('website_link', '')
    seeking_venue=request.form.get('seeking_venue')
    seeking_description=request.form.get('seeking_description', '')

    artist = Artist.query.get(artist_id)
    artist.name=name
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.genres=genres
    artist.image_link=image_link
    artist.facebook_link=facebook_link
    artist.website_link=website_link
    artist.seeking_venue=seeking_venue
    artist.seeking_description=seeking_description
    db.session.commit()
    flash("The artist " + request.form['name'] + 'detail was updated successful' )
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  except:
    db.session.rollback()
    flash("The artist" + request.form['name'] + "was not updated.Please try again")
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id).first()
  forms = VenueForm()
  forms.name.data=venue.name
  forms.city.data=venue.city
  forms.address.data=venue.address
  forms.phone.data=venue.phone
  forms.genres.data=venue.genres
  forms.image_link.data=venue.image_link
  forms.facebook_link.data=venue.facebook_link
  forms.website_link.data=venue.website_link
  forms.seeking_talent.data=venue.seeking_talent
  forms.seeking_description.data=venue.seeking_description
  return render_template('forms/edit_venue.html', form=forms, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:

    name = request.form.get('name','')
    city =request.form.get('city','')
    state=request.form.get('state','')
    address=request.form.get('address','')
    phone=request.form.get('phone','')
    genres=request.form.get('genres','')
    image_link= request.form.get('image_link','')
    facebook_link=request.form.get('facebook_link','')
    website_link=request.form.get('website_link','')
    seeking_talent=request.form.get('seeking_talent')
    seeking_description=request.form.get('seeking_description', '')
    venue =Venue.query.get(venue_id)
    venue.name =name
    venue.city=city
    venue.state=state
    venue.address=address
    venue.phone=phone
    venue.genres=genres
    venue.image_link=image_link
    venue.facebook_link=facebook_link
    venue.website_link=website_link
    venue.seeking_talent=seeking_talent
    venue.seeking_description=seeking_description
    db.session.commit()
    flash('Venue' + request.form['name'] + 'was successful updated')

  except:
    db.session.rollback()
    flash('Venue' + request.form['name'] + ' was not successful updated. Please try again' )
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ---------------------------------F-------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone= request.form.get('phone', '')
    genres = request.form.get('genres', '')
    image_link=request.form.get('image_link', '')
    facebook_link=request.form.get('facebook_link', '')
    website_link = request.form.get('website_link')
    seeking_venue=request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description', '')

    todo=Artist(
        name=name,
        city =city,
        state=state,
        phone=phone,
        genres=genres,
        image_link= image_link,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description
      )
    db.session.add(todo)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' was not successfully listed!')

  finally:
    db.session.close()
  return render_template('pages/home.html')
  
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  r


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  all_shows = Show.query.all()
  for data_show in all_shows:
    venue = Venue.query.filter_by(id=data_show.venue_id).first()
    artist= Artist.query.filter_by(id=data_show.artist_id).first()
    
    data.append({
      'venue_id':data_show.venue_id,
      'venue_name':venue.name,
      'artist_id':data_show.venue_id,
      'artist_name':artist.name,
      'artist_image_link':artist.image_link,
      'start_time':str(data_show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    start_time=request.form.get('start_time')
    todo = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )
    db.session.add(todo)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured Show was not successfully listed!')
  finally:
    db.session.close()
   
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  
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
