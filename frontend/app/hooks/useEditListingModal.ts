import { create } from 'zustand';

interface EditListingModalStore {
  isOpen: boolean;
  listing: any;
  onOpen: (listing: any) => void;
  onClose: () => void;
}

const useEditListingModal = create<EditListingModalStore>((set) => ({
  isOpen: false,
  listing: null,
  onOpen: (listing) => set({ isOpen: true, listing }),
  onClose: () => set({ isOpen: false, listing: null }),
}));

export default useEditListingModal;
