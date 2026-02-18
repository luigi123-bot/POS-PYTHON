import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pos_flutter/core/theme/app_theme.dart';
import 'package:pos_flutter/features/auth/providers/auth_provider.dart';

class AppDrawer extends ConsumerWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);
    final user = authState.user;
    final role = user?.role?.name ?? 'customer';

    return Drawer(
      child: Column(
        children: [
          // Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(20, 50, 20, 20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.primary, AppColors.primaryLight],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 35,
                  backgroundColor: Colors.white,
                  child: Text(
                    user?.fullName.substring(0, 1).toUpperCase() ?? 'U',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  user?.fullName ?? 'Usuario',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  user?.email ?? '',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    user?.role?.displayName ?? 'Usuario',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Menu items
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                _buildMenuItem(
                  context,
                  icon: Icons.dashboard,
                  title: 'Dashboard',
                  onTap: () => _navigate(context, '/admin'),
                ),
                if (role == 'admin' || role == 'superadmin' || role == 'cashier')
                  _buildMenuItem(
                    context,
                    icon: Icons.point_of_sale,
                    title: 'Punto de Venta',
                    onTap: () => _navigate(context, '/pos'),
                  ),
                if (role == 'admin' || role == 'superadmin')
                  _buildMenuItem(
                    context,
                    icon: Icons.inventory_2,
                    title: 'Productos',
                    onTap: () => _navigate(context, '/admin/products'),
                  ),
                if (role == 'admin' || role == 'superadmin')
                  _buildMenuItem(
                    context,
                    icon: Icons.receipt_long,
                    title: 'Ventas',
                    onTap: () => _navigate(context, '/admin/sales'),
                  ),
                if (role == 'admin' || role == 'superadmin')
                  _buildMenuItem(
                    context,
                    icon: Icons.people,
                    title: 'Usuarios',
                    onTap: () => _navigate(context, '/admin/users'),
                  ),
                if (role == 'admin' || role == 'superadmin')
                  _buildMenuItem(
                    context,
                    icon: Icons.store,
                    title: 'Sucursales',
                    onTap: () {},
                  ),
                if (role == 'admin' || role == 'superadmin')
                  _buildMenuItem(
                    context,
                    icon: Icons.bar_chart,
                    title: 'Reportes',
                    onTap: () {},
                  ),
                const Divider(),
                _buildMenuItem(
                  context,
                  icon: Icons.settings,
                  title: 'Configuración',
                  onTap: () {},
                ),
                _buildMenuItem(
                  context,
                  icon: Icons.help_outline,
                  title: 'Ayuda',
                  onTap: () {},
                ),
              ],
            ),
          ),

          // Logout
          Container(
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(color: AppColors.border),
              ),
            ),
            child: ListTile(
              leading: const Icon(Icons.logout, color: AppColors.error),
              title: const Text(
                'Cerrar Sesión',
                style: TextStyle(color: AppColors.error),
              ),
              onTap: () async {
                Navigator.pop(context);
                await ref.read(authStateProvider.notifier).logout();
                if (context.mounted) context.go('/login');
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: AppColors.textSecondary),
      title: Text(title),
      onTap: onTap,
    );
  }

  void _navigate(BuildContext context, String route) {
    Navigator.pop(context);
    context.go(route);
  }
}
