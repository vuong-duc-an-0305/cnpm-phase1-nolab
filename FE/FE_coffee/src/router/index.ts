import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

// Lazy-load views
const Login = () => import('../views/Login.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const Orders = () => import('../views/Orders.vue')
const OrderDetail = () => import('../views/OrderDetail.vue')
const NewOrder = () => import('../views/NewOrder.vue')
const Products = () => import('../views/Products.vue')
const ProductDetail = () => import('../views/ProductDetail.vue')
const Customers = () => import('../views/Customers.vue')
const CustomerDetail = () => import('../views/CustomerDetail.vue')
const Employees = () => import('../views/Employees.vue')
const Attendance = () => import('../views/Attendance.vue')
const Inventory = () => import('../views/Inventory.vue')
const Reports = () => import('../views/Reports.vue')
const AccessDenied = () => import('../views/AccessDenied.vue')
const NotFound = () => import('../views/NotFound.vue')

// Layout
const AppLayout = () => import('../components/layout/AppLayout.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { guestOnly: true },
    },
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: 'dashboard', name: 'dashboard', component: Dashboard, meta: { permission: 'dashboard' } },
        { path: 'orders', name: 'orders', component: Orders, meta: { permission: 'orders' } },
        { path: 'orders/:id', name: 'order-detail', component: OrderDetail, props: true, meta: { permission: 'orders' } },
        { path: 'new-order', name: 'new-order', component: NewOrder, meta: { permission: 'orders' } },
        { path: 'products', name: 'products', component: Products, meta: { permission: 'products' } },
        { path: 'products/:id', name: 'product-detail', component: ProductDetail, props: true, meta: { permission: 'products' } },
        { path: 'customers', name: 'customers', component: Customers, meta: { permission: 'customers' } },
        { path: 'customers/:id', name: 'customer-detail', component: CustomerDetail, props: true, meta: { permission: 'customers' } },
        { path: 'employees', name: 'employees', component: Employees, meta: { permission: 'employees' } },
        { path: 'attendance', name: 'attendance', component: Attendance, meta: { permission: 'employees' } },
        { path: 'inventory', name: 'inventory', component: Inventory, meta: { permission: 'inventory' } },
        { path: 'reports', name: 'reports', component: Reports, meta: { permission: 'reports' } },
      ],
    },
    {
      path: '/access-denied',
      name: 'access-denied',
      component: AccessDenied,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFound,
    },
  ],
})

// Navigation guards
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('auth_token')
  const userRole = localStorage.getItem('user_role')

  // Kiểm tra authentication
  if (to.meta?.requiresAuth && !token) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta?.guestOnly && token) {
    // Redirect dựa trên role
    if (userRole === 'cashier' || userRole === 'waiter') {
      return next({ name: 'orders' })
    } else {
      return next({ name: 'dashboard' })
    }
  }

  // Kiểm tra quyền truy cập
  if (to.meta?.permission && token) {
    const { hasPermission } = useAuth()
    
    if (!hasPermission(to.meta.permission as string)) {
      // Nếu không có quyền, redirect đến trang access denied
      return next({ name: 'access-denied' })
    }
  }

  return next()
})

export default router
