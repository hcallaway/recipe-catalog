from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurant/restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        try:
            ## Start Restaurants Page
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
                for restaurant in restaurants:
                    output += "<h3>{}</h3>".format(restaurant.name)
                    output += "</br>"
                    # Objective 2 -- Add Edit and Delete Links
                    output += "<a href ='/restaurants/{}/edit' >Edit </a> ".format(restaurant.id)
                    output += "</br>"
                    output += "<a href ='/restaurants/{}/delete'> Delete </a>".format(restaurant.id)
                    output += "</br></br></br>"
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Enter new restaurant here: </h1>"
                output += """<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"""
                output += """<input name='newRestaurantName' type='text' placeholder='New Restaurant Name'>"""
                output += """<input type='submit' value='Create'></form>"""
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/edit"):
                # Get ID from URL
                id = self.path.split('/')[2]
                updateRestaurant = session.query(Restaurant).filter_by(id = id).one()
                if id != []:
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Change {} to: </h1>".format(updateRestaurant.name)
                    output += """<form method='POST' enctype='multipart/form-data' action='/restaurants/{}/edit'>""".format(updateRestaurant.id)
                    output += """<input name='updatedRestaurantName' type='text' placeholder='New Name'>"""
                    output += """<input type='submit' value='Create'></form>"""
                    output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith('/delete'):
                id = self.path.split('/')[2]
                deleteRestaurant = session.query(Restaurant).filter_by(id = id).one()
                if deleteRestaurant:
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Delete {}?</h1>".format(deleteRestaurant.name)
                    output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/{}/delete'>".format(deleteRestaurant.id)
                    output += "<input type = 'submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            if self.path.endswith('/edit'):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('updatedRestaurantName')
                    id = self.path.split('/')[2]
                    updateRestaurant = session.query(Restaurant).filter_by(id = id).one()
                    if updateRestaurant != []:
                        updateRestaurant.name = messagecontent[0]
                        session.add(updateRestaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
            if self.path.endswith('/delete'):
                id = self.path.split('/')[2]
                deleteRestaurant = session.query(Restaurant).filter_by(id = id).one()
                if deleteRestaurant:
                    session.delete(deleteRestaurant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('content-type', 'text/html')
                    self.send_header('location', '/restaurants')
                    self.end_headers()
        except:
            pass


def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print('Web server running...open localhost:8080/restaurants in your browser')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()