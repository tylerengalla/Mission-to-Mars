from flask import Flask, render_template
from flask_pymongo import PyMongo
import scraping

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection 
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app" 
mongo = PyMongo(app)
                
# this route tells Flask what to display when we're looking at home 
# page, index.html 
@app.route("/")
# this function is what links our visual rep of our work, our web app,
# to the code that powers it 
def index():
    
    # uses PyMongo to find the "mars" collection in our database
    mars = mongo.db.mars.find_one()
    
    # tells Flask to return an HTML template using an index.html file 
    return render_template("index.html", mars=mars) # mars=mars tells 
                        # Python to use the "mars" collection in MDB


# This func will set up our scraping route
@app.route("/scrape")
def scrape():
    
    # assign variable pointing to db
    mars = mongo.db.mars
    
    # create new variable to hold the newly scraped data
    # in this line, we're referencing the scrape_all func in the py file
    mars_data = scraping.scrape_all()
    
    # now that we've gathered new data, need to update the db
    # format is as follows: .update(query_parameter, data, options)

    mars.update({}, mars_data, upsert=True)
    return "Scraping Successful!"

if __name__ == "__main__":
    app.run()



