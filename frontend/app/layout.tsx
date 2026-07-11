import { Nunito } from 'next/font/google';
import getCurrentUser from './actions/getCurrentUser';
import LoginModal from './components/modals/LoginModal';
import RegisterModal from './components/modals/RegisterModal';
import Navbar from './components/navbar/Navbar';
import './globals.css';
import ToasterProvider from './providers/ToasterProvider';
import RentModal from './components/modals/RentModal';
import SearchModal from './components/modals/SearchModal';
import EditListingModal from './components/modals/EditListingModal';
import ReviewModal from './components/modals/ReviewModal';

const inter = Nunito({ subsets: ['latin'] });

export const metadata = {
  title: 'Airbnb',
  description: 'Airbnb clone',
};

const RootLayout = async ({ children }: { children: React.ReactNode }) => {
  const currentUser = await getCurrentUser();

  return (
    <html lang="en">
      <head>
        <script dangerouslySetInnerHTML={{ __html: `
          (function() {
            try {
              var theme = localStorage.getItem('theme');
              if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                document.documentElement.classList.add('dark');
              } else {
                document.documentElement.classList.remove('dark');
              }
            } catch (e) {}
          })();
        ` }} />
      </head>
      <body className={`${inter.className} bg-white text-neutral-800 dark:bg-neutral-950 dark:text-neutral-100 transition-colors duration-200`}>
        <ToasterProvider />
        <LoginModal />
        <SearchModal />
        <RegisterModal />
        <RentModal />
        <EditListingModal />
        <ReviewModal />
        <Navbar currentUser={currentUser} />
        <div className="pb-20 pt-28">{children}</div>
      </body>
    </html>
  );
};

export default RootLayout;
