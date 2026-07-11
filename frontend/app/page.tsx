import getCurrentUser from './actions/getCurrentUser';
import getListings, { IListingsParams } from './actions/getListings';
import EmptyState from './components/EmptyState';
import HomeClient from './components/HomeClient';

export const dynamic = 'force-dynamic';

interface HomeProps {
  searchParams: IListingsParams;
}

const Home = async ({ searchParams }: HomeProps) => {
  const listings = await getListings(searchParams);
  const currentUser = await getCurrentUser();

  const isEmpty = listings.length === 0;

  if (isEmpty) {
    return <EmptyState showReset />;
  }

  return (
    <HomeClient listings={listings} currentUser={currentUser} />
  );
};

export default Home;
