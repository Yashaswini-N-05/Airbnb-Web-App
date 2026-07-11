'use client';

import L from 'leaflet';
import { MapContainer, Marker, TileLayer, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useRouter } from 'next/navigation';
import useCountries from '../hooks/useCountries';
import { SafeListing } from '../types';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon.src,
  iconRetinaUrl: markerIcon2x.src,
  shadowUrl: markerShadow.src,
});

interface ListingsMapProps {
  listings: SafeListing[];
}

const ListingsMap: React.FC<ListingsMapProps> = ({ listings }) => {
  const router = useRouter();
  const { getByValue } = useCountries();

  // Helper to hash and create deterministic jitter so pins in same country/city spread out
  const getJitteredCoords = (listing: SafeListing): L.LatLngExpression => {
    const country = getByValue(listing.locationValue);
    const baseCoords = country?.latlng || [38.0, -97.0]; // Default US center

    let hashLat = 0;
    let hashLng = 0;
    const key = listing.id;

    for (let i = 0; i < key.length; i++) {
      hashLat = key.charCodeAt(i) + ((hashLat << 5) - hashLat);
      hashLng = key.charCodeAt(i) * 31 + ((hashLng << 5) - hashLng);
    }

    const jitterLat = (Math.abs(hashLat) % 150 - 75) / 1000; // -0.075 to +0.075
    const jitterLng = (Math.abs(hashLng) % 150 - 75) / 1000; // -0.075 to +0.075

    return [baseCoords[0] + jitterLat, baseCoords[1] + jitterLng];
  };

  // Find center of map based on first listing, or fallback
  const mapCenter: L.LatLngExpression = listings.length > 0 
    ? (getByValue(listings[0].locationValue)?.latlng || [38.0, -97.0]) 
    : [38.0, -97.0];

  return (
    <div className="h-[75vh] w-full rounded-xl overflow-hidden relative shadow-md mt-6">
      <MapContainer
        center={mapCenter}
        zoom={5}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {listings.map((listing) => {
          const position = getJitteredCoords(listing);
          return (
            <Marker key={listing.id} position={position}>
              <Popup>
                <div 
                  onClick={() => router.push(`/listings/${listing.id}`)}
                  className="flex flex-col gap-2 w-48 cursor-pointer hover:opacity-90"
                >
                  <div className="relative h-28 w-full overflow-hidden rounded-md">
                    <img 
                      src={listing.imageSrc} 
                      className="object-cover w-full h-full" 
                      alt={listing.title} 
                    />
                  </div>
                  <div className="font-bold text-sm text-neutral-800 line-clamp-1">{listing.title}</div>
                  <div className="text-xs text-neutral-500 font-light">{listing.locationValue} • {listing.category}</div>
                  <div className="font-semibold text-sm text-neutral-900 mt-1">
                    ${listing.price} <span className="font-light text-xs text-neutral-500">/ night</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default ListingsMap;
