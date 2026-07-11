'use client';

import React, { useState } from 'react';
import { format } from 'date-fns';
import { Range } from 'react-date-range';
import Calendar from '../inputs/Calendar';
import { FiChevronDown, FiChevronUp } from 'react-icons/fi';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';

interface Props {
  price: number;
  totalPrice: number;
  onChangeDate: (value: Range) => void;
  dateRange: Range;
  onSubmit: () => void;
  disabled?: boolean;
  disabledDates: Date[];
}

const ListingReservation: React.FC<Props> = ({
  price,
  totalPrice,
  onChangeDate,
  dateRange,
  onSubmit,
  disabled,
  disabledDates,
}) => {
  const [showCalendar, setShowCalendar] = useState(false);
  const [showGuestDropdown, setShowGuestDropdown] = useState(false);
  const [guestCount, setGuestCount] = useState(1);

  const start = dateRange.startDate ? format(dateRange.startDate, 'M/d/yyyy') : 'Add date';
  const end = dateRange.endDate ? format(dateRange.endDate, 'M/d/yyyy') : 'Add date';
  const nights = dateRange.startDate && dateRange.endDate
    ? Math.max(1, Math.round((dateRange.endDate.getTime() - dateRange.startDate.getTime()) / (1000 * 60 * 60 * 24)))
    : 1;

  // Let's show a discount rate like in the screenshot if stay is >= 2 nights
  const hasDiscount = nights >= 2;
  const originalPrice = Math.round(totalPrice * 1.15);

  return (
    <div className="bg-white dark:bg-neutral-900 rounded-2xl border-[1px] border-neutral-200 dark:border-neutral-800 p-6 shadow-xl flex flex-col gap-4">
      {/* Price Section */}
      <div className="flex flex-row items-baseline gap-1">
        {hasDiscount && (
          <span className="line-through text-neutral-400 text-lg font-light mr-1">
            ₹{originalPrice.toLocaleString()}
          </span>
        )}
        <span className="text-2xl font-bold text-neutral-800 dark:text-neutral-100">
          ₹{totalPrice.toLocaleString()}
        </span>
        <span className="text-neutral-500 dark:text-neutral-400 text-sm font-light">
          for {nights} {nights === 1 ? 'night' : 'nights'}
        </span>
      </div>

      {/* Date & Guest Selection Grid */}
      <div className="border-[1px] border-neutral-300 dark:border-neutral-700 rounded-xl overflow-hidden bg-white dark:bg-neutral-900">
        {/* Top Row: Check-in / Checkout split */}
        <div className="grid grid-cols-2">
          <div 
            onClick={() => {
              setShowCalendar((prev) => !prev);
              setShowGuestDropdown(false);
            }}
            className="flex flex-col p-3 border-r-[1px] border-b-[1px] border-neutral-300 dark:border-neutral-700 cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800 transition"
          >
            <span className="text-[9px] font-extrabold text-neutral-800 dark:text-neutral-200 uppercase tracking-wider">CHECK-IN</span>
            <span className="text-sm text-neutral-600 dark:text-neutral-300 mt-0.5">{start}</span>
          </div>
          <div 
            onClick={() => {
              setShowCalendar((prev) => !prev);
              setShowGuestDropdown(false);
            }}
            className="flex flex-col p-3 border-b-[1px] border-neutral-300 dark:border-neutral-700 cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800 transition"
          >
            <span className="text-[9px] font-extrabold text-neutral-800 dark:text-neutral-200 uppercase tracking-wider">CHECKOUT</span>
            <span className="text-sm text-neutral-600 dark:text-neutral-300 mt-0.5">{end}</span>
          </div>
        </div>

        {/* Bottom Row: Guest selection */}
        <div 
          onClick={() => {
            setShowGuestDropdown((prev) => !prev);
            setShowCalendar(false);
          }}
          className="flex items-center justify-between p-3 cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800 transition"
        >
          <div className="flex flex-col">
            <span className="text-[9px] font-extrabold text-neutral-800 dark:text-neutral-200 uppercase tracking-wider">GUESTS</span>
            <span className="text-sm text-neutral-600 dark:text-neutral-300 mt-0.5">
              {guestCount} {guestCount === 1 ? 'guest' : 'guests'}
            </span>
          </div>
          {showGuestDropdown ? (
            <FiChevronUp className="text-neutral-500" size={18} />
          ) : (
            <FiChevronDown className="text-neutral-500" size={18} />
          )}
        </div>
      </div>

      {/* Guest Dropdown Selector Content */}
      {showGuestDropdown && (
        <div className="border-[1px] border-neutral-200 dark:border-neutral-800 p-4 rounded-xl bg-neutral-50 dark:bg-neutral-850 flex items-center justify-between shadow-inner">
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">Guests</span>
            <span className="text-xs text-neutral-500">Ages 13 or above</span>
          </div>
          <div className="flex items-center gap-3">
            <button 
              disabled={guestCount <= 1}
              onClick={() => setGuestCount((c) => c - 1)}
              className="w-8 h-8 rounded-full border border-neutral-300 dark:border-neutral-600 flex items-center justify-center text-lg font-medium hover:bg-neutral-100 dark:hover:bg-neutral-750 disabled:opacity-40 disabled:hover:bg-transparent transition"
            >
              -
            </button>
            <span className="text-sm font-semibold text-neutral-800 dark:text-neutral-200 w-4 text-center">{guestCount}</span>
            <button 
              onClick={() => setGuestCount((c) => c + 1)}
              className="w-8 h-8 rounded-full border border-neutral-300 dark:border-neutral-600 flex items-center justify-center text-lg font-medium hover:bg-neutral-100 dark:hover:bg-neutral-750 transition"
            >
              +
            </button>
          </div>
        </div>
      )}

      {/* Collapsible React Date Range Calendar */}
      {showCalendar && (
        <div className="border-[1px] border-neutral-250 dark:border-neutral-800 rounded-2xl p-2 bg-white dark:bg-neutral-850 shadow-inner overflow-hidden z-20">
          <Calendar 
            value={dateRange} 
            disabledDates={disabledDates} 
            onChange={(value) => onChangeDate(value.selection)} 
          />
          <button 
            onClick={() => setShowCalendar(false)} 
            className="w-full text-center text-xs font-semibold text-rose-500 hover:text-rose-600 pt-2 pb-1 border-t border-neutral-100 dark:border-neutral-750 mt-2"
          >
            Close Calendar
          </button>
        </div>
      )}

      {/* Submit button matching Rose/Magenta Airbnb theme */}
      <button
        disabled={disabled}
        onClick={onSubmit}
        className="w-full py-3.5 bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 text-white font-bold rounded-xl transition duration-200 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed text-center shadow-md shadow-rose-500/10 hover:shadow-lg"
      >
        Reserve
      </button>

      <span className="text-center text-xs text-neutral-500 font-light mt-1">
        You won&apos;t be charged yet
      </span>
    </div>
  );
};

export default ListingReservation;
