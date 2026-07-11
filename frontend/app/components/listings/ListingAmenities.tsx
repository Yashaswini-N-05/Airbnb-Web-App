'use client';

import React from 'react';
import { 
  TbBath, TbWind, TbShirt, TbDeviceTv, TbSnowflake, TbDeviceLaptop, 
  TbToolsKitchen, TbParking, TbVideo, TbAlertTriangle, TbLock, TbFlameOff, TbKey
} from 'react-icons/tb';
import { MdOutlineLocalLaundryService, MdOutlineSafetyCheck } from 'react-icons/md';
import { BiCameraHome, BiFirstAid } from 'react-icons/bi';
import { FiWifi } from 'react-icons/fi';

interface AmenityItem {
  name: string;
  detail?: string;
  unavailable?: boolean;
}

interface AmenityCategory {
  title: string;
  icon: React.ComponentType<any>;
  items: AmenityItem[];
}

const amenityCategories: AmenityCategory[] = [
  {
    title: 'Bathroom',
    icon: TbBath,
    items: [
      { name: 'Bath' },
      { name: 'Hairdryer' },
      { name: 'Shampoo' },
      { name: 'Body soap' },
      { name: 'Outdoor shower' },
      { name: 'Hot water' },
      { name: 'Shower gel' }
    ]
  },
  {
    title: 'Bedroom and laundry',
    icon: MdOutlineLocalLaundryService,
    items: [
      { name: 'Washing machine' },
      { name: 'Essentials', detail: 'Towels, bed sheets, soap and toilet paper' },
      { name: 'Hangers' },
      { name: 'Bed linen' },
      { name: 'Cotton linen' },
      { name: 'Extra pillows and blankets' },
      { name: 'Room-darkening blinds' },
      { name: 'Iron' },
      { name: 'Clothes drying rack' },
      { name: 'Clothes storage: wardrobe' }
    ]
  },
  {
    title: 'Entertainment',
    icon: TbDeviceTv,
    items: [
      { name: 'Ethernet connection' },
      { name: 'TV' },
      { name: 'Books and reading material' }
    ]
  },
  {
    title: 'Heating and cooling',
    icon: TbSnowflake,
    items: [
      { name: 'Air conditioning' },
      { name: 'Ceiling fan' }
    ]
  },
  {
    title: 'Home safety',
    icon: BiCameraHome,
    items: [
      { name: 'Exterior security cameras on property', detail: 'At the entrance, wall facing the pool, backyard, and kitchen entrance' },
      { name: 'First aid kit' }
    ]
  },
  {
    title: 'Internet and office',
    icon: FiWifi,
    items: [
      { name: 'Fast wifi – 110 Mbps', detail: 'Verified by speed test. Stream 4K videos and join video calls.' }
    ]
  },
  {
    title: 'Kitchen and dining',
    icon: TbToolsKitchen,
    items: [
      { name: 'Kitchen', detail: 'Space where guests can cook their own meals' },
      { name: 'LG refrigerator' },
      { name: 'Cooking basics', detail: 'Pots and pans, oil, salt and pepper' },
      { name: 'Crockery and cutlery', detail: 'Bowls, chopsticks, plates, cups, etc.' },
      { name: 'Freezer' },
      { name: 'Oven' },
      { name: 'Wine glasses' },
      { name: 'Blender' },
      { name: 'Dining table' }
    ]
  },
  {
    title: 'Outdoor',
    icon: TbWind,
    items: [
      { name: 'Outdoor furniture' }
    ]
  },
  {
    title: 'Parking and facilities',
    icon: TbParking,
    items: [
      { name: 'Free parking on premises' }
    ]
  },
  {
    title: 'Services',
    icon: TbKey,
    items: [
      { name: 'Self check-in' },
      { name: 'Lockbox' }
    ]
  },
  {
    title: 'Not included',
    icon: TbFlameOff,
    items: [
      { name: 'Smoke alarm', detail: 'This place may not have a smoke detector. Contact host.', unavailable: true },
      { name: 'Carbon monoxide alarm', detail: 'This place may not have a carbon monoxide detector.', unavailable: true },
      { name: 'Private entrance', unavailable: true },
      { name: 'Heating', unavailable: true }
    ]
  }
];

const ListingAmenities = () => {
  return (
    <div className="flex flex-col gap-6">
      <hr />
      <div className="text-xl font-semibold">What this place offers</div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4">
        {amenityCategories.map((category) => {
          const CategoryIcon = category.icon;
          return (
            <div key={category.title} className="flex flex-col gap-3">
              <div className="flex items-center gap-2 font-semibold text-neutral-800 border-b pb-1">
                <CategoryIcon className="text-neutral-600" size={20} />
                <span>{category.title}</span>
              </div>
              
              <ul className="flex flex-col gap-2 pl-6">
                {category.items.map((item, idx) => (
                  <li 
                    key={idx} 
                    className={`text-sm ${item.unavailable ? 'line-through text-neutral-400' : 'text-neutral-600'}`}
                  >
                    <div className="font-medium">{item.name}</div>
                    {item.detail && (
                      <div className={`text-xs ${item.unavailable ? 'text-neutral-400' : 'text-neutral-500'} mt-0.5`}>
                        {item.detail}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ListingAmenities;
