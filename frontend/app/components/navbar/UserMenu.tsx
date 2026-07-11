'use client';

import useLoginModal from '@/app/hooks/useLoginModal';
import { SafeUser } from '@/app/types';
import { useCallback, useEffect, useState } from 'react';
import { AiOutlineMenu } from 'react-icons/ai';
import useRegisterModal from '../../hooks/useRegisterModal';
import Avatar from '../Avatar';
import MenuItem from './MenuItem';
import useRentModal from '@/app/hooks/useRentModal';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { BsSun, BsMoon } from 'react-icons/bs';

interface Props {
  currentUser: SafeUser | null;
}

const UserMenu: React.FC<Props> = ({ currentUser }) => {
  const registerModal = useRegisterModal();
  const loginModal = useLoginModal();
  const rentModal = useRentModal();

  const router = useRouter();

  const [isOpen, setIsOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check dark mode state on mount
    setIsDark(document.documentElement.classList.contains('dark'));
  }, []);

  const toggleDarkMode = useCallback(() => {
    if (document.documentElement.classList.contains('dark')) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDark(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDark(true);
    }
  }, []);

  const toggleOpen = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const onRent = useCallback(() => {
    if (!currentUser) {
      return loginModal.onOpen();
    }
    rentModal.onOpen();
  }, [currentUser, loginModal, rentModal]);

  return (
    <div className="relative">
      <div className="flex flex-row items-center gap-3">
        <div
          className="hidden md:block text-sm font-semibold py-3 px-4 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-800 transition cursor-pointer text-neutral-800 dark:text-neutral-200"
          onClick={onRent}
        >
          Airbnb your home
        </div>
        <button
          onClick={toggleDarkMode}
          className="p-3 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-full transition cursor-pointer"
        >
          {isDark ? <BsSun size={18} /> : <BsMoon size={18} />}
        </button>
        <div
          className="p-4 md:py-1 md:px-2 border-[1px] border-neutral-200 dark:border-neutral-700 flex flex-row items-center gap-3 rounded-full cursor-pointer hover:shadow-md transition bg-white dark:bg-neutral-900"
          onClick={toggleOpen}
        >
          <AiOutlineMenu className="text-neutral-600 dark:text-neutral-300" />
          <div className="hidden md:block">
            <Avatar src={currentUser?.image} />
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="absolute rounded-xl shadow-md w-[40vw] md:w-3/4 bg-white dark:bg-neutral-900 overflow-hidden right-0 top-12 text-sm border dark:border-neutral-800">
          <div className="flex flex-col cursor-pointer text-neutral-800 dark:text-neutral-200">
            {currentUser ? (
              <>
                <MenuItem
                  onClick={() => {
                    router.push('/trips');
                  }}
                  label="My trips"
                />
                <MenuItem
                  onClick={() => {
                    router.push('/favorites');
                  }}
                  label="My favorites"
                />
                <MenuItem
                  onClick={() => {
                    router.push('/reservations');
                  }}
                  label="My reservations"
                />
                <MenuItem
                  onClick={() => {
                    router.push('/properties');
                  }}
                  label="My properties"
                />
                <MenuItem onClick={rentModal.onOpen} label="Airbnb my home" />
                <hr />
                <MenuItem onClick={() => toast.success("Logout simulated")} label="Logout" />
              </>
            ) : (
              <>
                <MenuItem onClick={loginModal.onOpen} label="Login" />
                <MenuItem onClick={registerModal.onOpen} label="Sign up" />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
