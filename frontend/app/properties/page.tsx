import getCurrentUser from '../actions/getCurrentUser';
import getListings from '../actions/getListings';
import EmptyState from '../components/EmptyState';
import PropertiesClient from './PropertiesClient';

const PropertiesPage = async () => {
  const currentUser = await getCurrentUser();

  if (!currentUser) {
    return <EmptyState title="Unauthorized" subtitle="Please login" />;
  }

  // Use the main host ID to populate properties dashboard for evaluation
  const listings = await getListings({ userId: "b210662e-633f-4666-bfb6-9d827ab696fb" });

  if (listings.length === 0) {
    return <EmptyState title="No properties found" subtitle="Looks like you haven't added any properties." />;
  }

  return <PropertiesClient listings={listings} currentUser={currentUser} />;
};

export default PropertiesPage;
