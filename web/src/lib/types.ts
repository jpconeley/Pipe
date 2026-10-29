export type ProductType = "pipe" | "valve" | "fitting" | "flange";
export type Manufacture = "seamless" | "welded" | "erw" | "na";
export type EndType = "plain_end" | "beveled" | "threaded" | "flanged" | "socket_weld" | "na";
export type Condition = "new_surplus" | "used_good" | "used_as_is";
export type ListingStatus = "open" | "partially_filled" | "filled" | "cancelled";
export type SubstitutionType = "exact" | "substitute";

export type Location = {
  id: number;
  name: string;
  city: string;
  state: string;
  lat: number;
  lon: number;
};

export type Ask = {
  id: number;
  seller_name: string;
  location_id: number;
  location: Location;
  product_type: ProductType;
  nominal_size_in: number;
  schedule_class: string;
  grade: string;
  manufacture: Manufacture;
  end_type: EndType;
  condition: Condition;
  has_mtr: boolean;
  quantity: number;
  unit: string;
  price_per_unit: number;
  quantity_filled: number;
  quantity_available: number;
  status: ListingStatus;
  created_at: string;
};

export type Bid = {
  id: number;
  buyer_name: string;
  destination_location_id: number;
  destination: Location;
  product_type: ProductType;
  nominal_size_in: number;
  schedule_class: string;
  grade: string;
  end_type: EndType;
  min_condition: Condition;
  require_mtr: boolean;
  quantity: number;
  unit: string;
  max_delivered_price_per_unit: number | null;
  quantity_filled: number;
  quantity_remaining: number;
  status: ListingStatus;
  created_at: string;
};

export type Match = {
  ask: Ask;
  matched_quantity: number;
  substitution_type: SubstitutionType;
  discount_pct: number;
  substitution_note: string;
  distance_miles: number | null;
  freight_per_unit: number;
  price_per_unit_fob: number;
  delivered_price_per_unit: number;
};

export type Trade = {
  id: number;
  ask_id: number;
  bid_id: number;
  product_type: ProductType;
  nominal_size_in: number;
  schedule_class: string;
  grade: string;
  substitution_type: SubstitutionType;
  quantity: number;
  unit: string;
  price_per_unit_fob: number;
  freight_per_unit: number;
  delivered_price_per_unit: number;
  origin_location_id: number;
  destination_location_id: number;
  traded_at: string;
};

export type GradeSubstitution = {
  base_grade: string;
  sub_grade: string;
  bidirectional: boolean;
  discount_pct: number;
  note: string;
};

export type Reference = {
  product_types: string[];
  nominal_sizes_in: number[];
  schedules: string[];
  grades: string[];
  manufactures: string[];
  end_types: string[];
  conditions: string[];
  grade_substitutions: GradeSubstitution[];
};

export type Dashboard = {
  open_asks: number;
  open_bids: number;
  trades_30d: number;
  volume_30d_units: number;
  recent_trades: Trade[];
};
