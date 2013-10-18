#get geocode from here https://pypi.python.org/pypi/pygeocoder
from pygeocoder import Geocoder
import sys 
from sets import Set
import time
import pygeolib
import math
import underscore
from retry import retry


def midway(p1, p2):
   x = (p1[0]+p2[0])/2
   y = (p1[1]+p2[1])/2
   return  (x,y)

@retry(Exception)
def get_state(point):
	return Geocoder.reverse_geocode(point[0],point[1]).state

def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
            
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    #  multiply arc by the radius of the earth 
    # in miles to get length.
    return arc * 3963.1676 #rad in miles

def same_state(p1, p2):
	#true if the two points are in the same state or if they are 50 miles apart; 
	#50 is an arbitraty number where we can assume no states will be inbetween the points
	s1 = get_state(p1)
	s2 = get_state(p2)
	dist = distance_on_unit_sphere(p1[0],p1[1],p2[0],p2[1])
 	return s1 == s2 or dist <=50

stts = Set()

#this is like binary search, we get the state of two points, if they are the same we stop
#otherwise look at states of the initial points and a halfway point
def point_states(p1, p2):
	time.sleep(3)
	s1 = get_state(p1)
	s2 = get_state(p2)
	#check if the addr1 and addr2 are in the same state, if they are we are done!
	if same_state(p1,p2):
		stts.add(s1)
		return stts
	#if two points not in two states, check states of initial points and midway point	
	else:
	  if s1:
	  	stts.add(s1)
	  if s2:
	    stts.add(s2)
	  m = midway(p1,p2)
	  ms = get_state(m)
	  if ms != s1:
	  	point_states(p1,m)
	  if ms != s2:
	  	point_states(m,p2)

#Converts the initial adresses to lat,long points and passes it to the point_States function
@retry(Exception)	
def states(addr1, addr2):	
		p1 = Geocoder.geocode(addr1)[0].coordinates
		p2 = Geocoder.geocode(addr2)[0].coordinates
		point_states(p1,p2)


if __name__ == "__main__":
	states(sys.argv[1], sys.argv[2])
