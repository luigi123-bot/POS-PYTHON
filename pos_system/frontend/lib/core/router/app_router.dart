import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pos_flutter/features/auth/presentation/screens/login_screen.dart';
import 'package:pos_flutter/features/auth/presentation/screens/splash_screen.dart';
import 'package:pos_flutter/features/auth/providers/auth_provider.dart';
import 'package:pos_flutter/features/dashboard/presentation/screens/admin_dashboard.dart';
import 'package:pos_flutter/features/dashboard/presentation/screens/cashier_dashboard.dart';
import 'package:pos_flutter/features/dashboard/presentation/screens/delivery_dashboard.dart';
import 'package:pos_flutter/features/dashboard/presentation/screens/customer_dashboard.dart';
import 'package:pos_flutter/features/pos/presentation/screens/pos_screen.dart';
import 'package:pos_flutter/features/products/presentation/screens/products_screen.dart';
import 'package:pos_flutter/features/sales/presentation/screens/sales_screen.dart';
import 'package:pos_flutter/features/users/presentation/screens/users_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);
  
  return GoRouter(
    initialLocation: '/splash',
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isLoggingIn = state.matchedLocation == '/login';
      final isSplash = state.matchedLocation == '/splash';
      
      if (isSplash) return null;
      
      if (!isLoggedIn && !isLoggingIn) {
        return '/login';
      }
      
      if (isLoggedIn && isLoggingIn) {
        // Redirect based on role
        final role = authState.user?.role?.name ?? 'customer';
        return _getDashboardRoute(role);
      }
      
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      
      // Admin Routes
      GoRoute(
        path: '/admin',
        builder: (context, state) => const AdminDashboard(),
      ),
      GoRoute(
        path: '/admin/users',
        builder: (context, state) => const UsersScreen(),
      ),
      GoRoute(
        path: '/admin/products',
        builder: (context, state) => const ProductsScreen(),
      ),
      GoRoute(
        path: '/admin/sales',
        builder: (context, state) => const SalesScreen(),
      ),
      
      // Cashier Routes
      GoRoute(
        path: '/cashier',
        builder: (context, state) => const CashierDashboard(),
      ),
      GoRoute(
        path: '/pos',
        builder: (context, state) => const POSScreen(),
      ),
      
      // Delivery Routes
      GoRoute(
        path: '/delivery',
        builder: (context, state) => const DeliveryDashboard(),
      ),
      
      // Customer Routes
      GoRoute(
        path: '/customer',
        builder: (context, state) => const CustomerDashboard(),
      ),
    ],
  );
});

String _getDashboardRoute(String role) {
  switch (role) {
    case 'superadmin':
    case 'admin':
      return '/admin';
    case 'cashier':
      return '/cashier';
    case 'delivery':
      return '/delivery';
    case 'customer':
      return '/customer';
    default:
      return '/login';
  }
}
