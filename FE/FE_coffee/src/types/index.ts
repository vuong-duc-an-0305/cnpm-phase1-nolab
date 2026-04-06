// Base Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// User & Auth Types
export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'cashier' | 'manager';
  isActive: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

// Category Types
export interface Category {
  CategoryID: number;
  CategoryName: string;
  product_count?: number;
}

// Product Types
export interface Product {
  ProductID: number;
  ProductName: string;
  Price: string;
  ImageUrl?: string;
  CategoryID: number;
  category_name?: string;
  Status: number;
  status_display?: string;
  is_available?: boolean;
  ingredients?: Array<{
    IngredientID: number;
    IngredientName: string;
    IngredientUnit?: string; // đơn vị của nguyên liệu trong kho
    Quantity: string; // định mức/1 sản phẩm
    Unit: string;
    QuantityInStock: string; // tồn hiện tại
  }>;
}

export interface ProductForm {
  ProductName: string;
  Price: number;
  ImageUrl?: string;
  CategoryID: number;
  Status: number;
}

// Ingredient Types
export interface Ingredient {
  IngredientID: number;
  IngredientName: string;
  Unit?: string;
  QuantityInStock: string;
  MinQuantity: string;
  is_low_stock?: boolean;
  stock_percentage?: number;
}

export interface IngredientForm {
  IngredientName: string;
  Unit?: string;
  QuantityInStock: number;
  MinQuantity: number;
}

// Recipe Types
export interface Recipe {
  ProductID: number;
  product_name?: string;
  IngredientID: number;
  ingredient_name?: string;
  ingredient_stock?: string;
  Quantity: string;
  Unit: string;
}

export interface RecipeForm {
  ProductID: number;
  IngredientID: number;
  Quantity: number;
  Unit: string;
}

// Customer Types
export interface Customer {
  CustomerID: number;
  FullName: string;
  PhoneNumber: string;
  Email?: string;
  RegisterDate?: string;
  LoyaltyPoints: number;
  membership_level?: string;
  total_orders?: number;
  total_spent?: string;
}

export interface CustomerForm {
  FullName: string;
  PhoneNumber: string;
  Email?: string;
}

export interface CustomerPointsForm {
  points: number;
  note?: string;
}

export interface CustomerOrderHistory {
  OrderID: number;
  OrderDate: string;
  TotalAmount: string;
  Status: string;
  status_display?: string;
  items_count?: number;
}

// Employee Types
export interface Employee {
  EmployeeID: number;
  FullName: string;
  PhoneNumber: string;
  JobTitle: string;
  WorkShift: 'SANG' | 'CHIEU' | 'TOI' | 'FULL';
  work_shift_display?: string;
}

export interface EmployeeForm {
  FullName: string;
  PhoneNumber: string;
  JobTitle: string;
  WorkShift: 'SANG' | 'CHIEU' | 'TOI' | 'FULL';
}

// Order Types
export interface OrderItem {
  ProductID: number;
  Quantity: number;
  ToppingNote?: string;
}

export interface Order {
  OrderID: number;
  CustomerID?: number;
  customer_name?: string;
  EmployeeID: number;
  employee_name?: string;
  OrderDate: string;
  TotalAmount: string;
  Discount: string;
  FinalAmount: string;
  PaymentMethod: 'CASH' | 'CARD' | 'MOMO' | 'BANKING';
  Status: 'PENDING' | 'PREPARING' | 'COMPLETED' | 'CANCELLED';
  status_display?: string;
  payment_method_display?: string;
  items_count?: number;
  order_details?: OrderDetail[];
}

export interface OrderDetail {
  OrderDetailID: number;
  ProductID: number;
  product_name?: string;
  Quantity: number;
  UnitPrice: string;
  Subtotal: string;
  ToppingNote?: string;
}

export interface OrderForm {
  CustomerID?: number;
  EmployeeID: number;
  PaymentMethod: 'CASH' | 'CARD' | 'MOMO' | 'BANKING';
  Discount: number;
  items: OrderItem[];
}

// Inventory Types
export interface ImportItem {
  IngredientID: number;
  Quantity: number;
  UnitPrice: number;
}

export interface Import {
  ImportID: number;
  EmployeeID: number;
  employee_name?: string;
  ImportDate: string;
  TotalAmount: string;
  items_count?: number;
  import_details?: ImportDetail[];
}

export interface ImportDetail {
  ImportID: number;
  IngredientID: number;
  ingredient_name?: string;
  Quantity: string;
  UnitPrice: string;
  subtotal: string;
}

export interface ImportForm {
  EmployeeID: number;
  items: ImportItem[];
}

// Dashboard & Stats Types
export interface DashboardStats {
  total_orders: number;
  total_revenue: string;
  total_customers: number;
  total_products: number;
  revenue_growth: number;
  orders_growth: number;
  customers_growth: number;
  products_growth: number;
}

export interface RevenueStats {
  summary: {
    total_orders: number;
    total_revenue: string;
    total_discount: string;
    average_order_value: string;
  };
  daily: Array<{
    date: string;
    orders: number;
    revenue: string;
  }>;
}

export interface BestSellingProduct {
  ProductID: number;
  ProductID__ProductName: string;
  total_quantity: number;
  total_revenue: string;
  order_count: number;
}

// Filter & Search Types
export interface FilterOptions {
  search?: string;
  category_id?: number;
  status?: string;
  from_date?: string;
  to_date?: string;
  page?: number;
  page_size?: number;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  loadingMessage?: string;
}

export interface ErrorState {
  hasError: boolean;
  errorMessage?: string;
  errorDetails?: any;
}

// Component Props Types
export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>;
}

// Notification Types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

// Form Validation Types
export interface ValidationRule {
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean | string;
}

export interface FormErrors {
  [key: string]: string[];
}
