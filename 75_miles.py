from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from typing import Dict, Tuple
import json

def get_coordinates(zipcode: str, geolocator: Nominatim) -> Tuple[float, float]:
    """
    Get coordinates for a single zipcode.
    Returns tuple of (latitude, longitude) or None if not found.
    """
    try:
        # Add FL, USA to improve accuracy of results
        location = geolocator.geocode(f"{zipcode}, FL, USA", timeout=30)
        if location:
            return (location.latitude, location.longitude)
        return None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Error getting coordinates for {zipcode}: {str(e)}")
        return None

def generate_coordinates_dict(zipcodes: list[str]) -> Dict[str, Tuple[float, float]]:
    """
    Generate a dictionary of zipcode coordinates.
    Returns dict with zipcode as key and (lat, lon) tuple as value.
    """
    # Initialize geocoder
    geolocator = Nominatim(user_agent="fl_zipcode_finder", timeout=30)
    coordinates_dict = {}
    total = len(zipcodes)
    
    print(f"Processing {total} zip codes...")
    
    for i, zipcode in enumerate(zipcodes, 1):
        print(f"Processing {zipcode} ({i}/{total})...")
        
        # Try up to 3 times for each zipcode
        for attempt in range(3):
            coords = get_coordinates(zipcode, geolocator)
            if coords:
                coordinates_dict[zipcode] = coords
                print(f"✓ Found coordinates for {zipcode}: {coords}")
                break
            else:
                if attempt < 2:  # Only print retry message if we're going to retry
                    print(f"Retry {attempt + 1}/3 for {zipcode}")
                    time.sleep(2)  # Wait before retrying
                else:
                    print(f"✗ Could not find coordinates for {zipcode} after 3 attempts")
        
        # Wait between zipcodes to respect rate limits
        time.sleep(1)
    
    return coordinates_dict

def main():
    # List of Florida zip codes
    zipcodes = [
        "34734", "34736", "34737", "34739", "34741", "34743", "34744", "34746", "34747",
        "34748", "34753", "34756", "34758", "34759", "34761", "34762", "34769", "34771",
        "34772", "34773", "34785", "34786", "34787", "34788", "34797", "34945", "34946",
        "34947", "34949", "34950", "34951", "34952", "34953", "34956", "34957", "34972",
        "34974", "34981", "34982", "34983", "34984", "34986", "34987", "34990", "34994",
        "34996", "34997"
    ]
    
    # Remove duplicates while maintaining order
    zipcodes = list(dict.fromkeys(zipcodes))
    
    # Generate coordinates
    coordinates = generate_coordinates_dict(zipcodes)
    
    # Save to JSON file
    output_file = 'florida_coordinates.json'
    with open(output_file, 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print(f"\nProcessed {len(coordinates)} zip codes successfully")
    print(f"Results saved to {output_file}")
    
    # Print the coordinates
    print("\nZipcode Coordinates:")
    print("Zipcode  | Coordinates")
    print("-" * 35)
    for zipcode, coords in coordinates.items():
        print(f"{zipcode}    | {coords}")

if __name__ == "__main__":
    main()

