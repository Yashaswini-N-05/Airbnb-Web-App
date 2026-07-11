import { create } from 'zustand';

interface ReviewModalStore {
  isOpen: boolean;
  listingId: string;
  onOpen: (listingId: string) => void;
  onClose: () => void;
}

const useReviewModal = create<ReviewModalStore>((set) => ({
  isOpen: false,
  listingId: '',
  onOpen: (listingId) => set({ isOpen: true, listingId }),
  onClose: () => set({ isOpen: false, listingId: '' }),
}));

export default useReviewModal;
