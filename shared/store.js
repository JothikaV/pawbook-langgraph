/**
 * shared/store.js
 * In-memory data store shared across MCP servers via require cache.
 * In production this would be Redis or a database.
 */

const { v4: uuidv4 } = require('uuid');

// ─── Groomers ────────────────────────────────────────────────
const groomers = [
  { id: 'g1', name: 'Sarah Chen',    specialties: ['dog', 'cat'],    rating: 4.9 },
  { id: 'g2', name: 'Marcus Rivera', specialties: ['dog', 'rabbit'], rating: 4.8 },
  { id: 'g3', name: 'Priya Nair',    specialties: ['cat'],           rating: 4.9 },
  { id: 'g4', name: 'Tom Walsh',     specialties: ['dog'],           rating: 4.7 },
];

// ─── Slots ───────────────────────────────────────────────────
function generateSlots() {
  const store = {};
  const times = ['9:00 AM', '10:30 AM', '12:00 PM', '2:00 PM', '3:30 PM', '5:00 PM', '6:30 PM'];
  const now   = new Date();

  for (let d = 0; d < 7; d++) {
    const date = new Date(now);
    date.setDate(now.getDate() + d);
    const dateStr = date.toISOString().split('T')[0];

    groomers.forEach(groomer => {
      times.forEach((time, i) => {
        if (Math.random() > 0.3) {
          const id = `slot-${dateStr}-${groomer.id}-${i}`;
          store[id] = {
            id, date: dateStr, time,
            groomerId:   groomer.id,
            groomerName: groomer.name,
            status: Math.random() > 0.55 ? 'available' : 'booked',
          };
        }
      });
    });
  }
  return store;
}

const slots    = generateSlots();
const bookings = {};
const notificationLog = [];

// ─── Pricing ─────────────────────────────────────────────────
const pricingMatrix = {
  dog:    { small: { basic:35, full:60, bath_only:25 }, medium: { basic:45, full:75, bath_only:35 }, large: { basic:55, full:90, bath_only:45 }, giant: { basic:70, full:110, bath_only:55 } },
  cat:    { small: { basic:40, full:65, bath_only:30 }, medium: { basic:50, full:75, bath_only:38 }, large: { basic:60, full:85, bath_only:45 } },
  rabbit: { small: { basic:30, full:50, bath_only:20 }, medium: { basic:38, full:60, bath_only:28 } },
};

const addOns = {
  nail_trim:      { name: 'Nail Trimming',  price: 10 },
  teeth_brushing: { name: 'Teeth Brushing', price: 12 },
  flea_treatment: { name: 'Flea Treatment', price: 20 },
  bow_accessory:  { name: 'Bow / Bandana',  price: 5  },
  paw_balm:       { name: 'Paw Balm',       price: 8  },
};

module.exports = { groomers, slots, bookings, notificationLog, pricingMatrix, addOns, uuidv4 };
