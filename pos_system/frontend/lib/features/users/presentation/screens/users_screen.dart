import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pos_flutter/core/theme/app_theme.dart';

class UsersScreen extends ConsumerStatefulWidget {
  const UsersScreen({super.key});

  @override
  ConsumerState<UsersScreen> createState() => _UsersScreenState();
}

class _UsersScreenState extends ConsumerState<UsersScreen> {
  final _searchController = TextEditingController();
  String _roleFilter = 'all';

  // Demo users
  final List<Map<String, dynamic>> _users = [
    {
      'id': 1,
      'name': 'Administrador del Sistema',
      'username': 'admin',
      'email': 'admin@posystem.com',
      'role': 'superadmin',
      'roleName': 'Super Administrador',
      'branch': 'Sucursal Principal',
      'active': true,
      'lastLogin': '18/02/2024 10:30',
    },
    {
      'id': 2,
      'name': 'Juan Pérez',
      'username': 'cajero1',
      'email': 'cajero1@posystem.com',
      'role': 'cashier',
      'roleName': 'Cajero',
      'branch': 'Sucursal Principal',
      'active': true,
      'lastLogin': '18/02/2024 09:00',
    },
    {
      'id': 3,
      'name': 'Carlos López',
      'username': 'repartidor1',
      'email': 'repartidor1@posystem.com',
      'role': 'delivery',
      'roleName': 'Repartidor',
      'branch': 'Sucursal Principal',
      'active': true,
      'lastLogin': '18/02/2024 08:30',
    },
    {
      'id': 4,
      'name': 'María García',
      'username': 'cliente1',
      'email': 'cliente1@posystem.com',
      'role': 'customer',
      'roleName': 'Cliente',
      'branch': '-',
      'active': true,
      'lastLogin': '17/02/2024 15:00',
    },
  ];

  Color _getRoleColor(String role) {
    switch (role) {
      case 'superadmin':
        return Colors.purple;
      case 'admin':
        return AppColors.primary;
      case 'cashier':
        return AppColors.success;
      case 'delivery':
        return AppColors.warning;
      case 'customer':
        return AppColors.info;
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Usuarios'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showUserDialog,
        icon: const Icon(Icons.person_add),
        label: const Text('Nuevo Usuario'),
      ),
      body: Column(
        children: [
          // Stats and filters
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Stats
                _buildStatCard('Total Usuarios', '${_users.length}', Icons.people, AppColors.primary),
                const SizedBox(width: 12),
                _buildStatCard('Activos', '${_users.where((u) => u['active']).length}', Icons.check_circle, AppColors.success),
                const SizedBox(width: 12),
                _buildStatCard('Cajeros', '${_users.where((u) => u['role'] == 'cashier').length}', Icons.point_of_sale, AppColors.warning),
                const Spacer(),
                // Search and filter
                SizedBox(
                  width: 250,
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      hintText: 'Buscar usuario...',
                      prefixIcon: Icon(Icons.search),
                      isDense: true,
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                ),
                const SizedBox(width: 16),
                DropdownButton<String>(
                  value: _roleFilter,
                  items: const [
                    DropdownMenuItem(value: 'all', child: Text('Todos los roles')),
                    DropdownMenuItem(value: 'superadmin', child: Text('Super Admin')),
                    DropdownMenuItem(value: 'admin', child: Text('Administrador')),
                    DropdownMenuItem(value: 'cashier', child: Text('Cajero')),
                    DropdownMenuItem(value: 'delivery', child: Text('Repartidor')),
                    DropdownMenuItem(value: 'customer', child: Text('Cliente')),
                  ],
                  onChanged: (value) {
                    setState(() => _roleFilter = value!);
                  },
                ),
              ],
            ),
          ),

          // Users grid
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  childAspectRatio: 1.8,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                ),
                itemCount: _users.length,
                itemBuilder: (context, index) {
                  final user = _users[index];
                  return _buildUserCard(user);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildUserCard(Map<String, dynamic> user) {
    final roleColor = _getRoleColor(user['role']);
    
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => _showUserDialog(user: user),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    CircleAvatar(
                      radius: 24,
                      backgroundColor: roleColor.withOpacity(0.1),
                      child: Text(
                        user['name'].substring(0, 1).toUpperCase(),
                        style: TextStyle(
                          color: roleColor,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            user['name'],
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            '@${user['username']}',
                            style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: user['active'] ? AppColors.success : AppColors.error,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ],
                ),
                const Spacer(),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: roleColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        user['roleName'],
                        style: TextStyle(
                          fontSize: 11,
                          color: roleColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const Spacer(),
                    Icon(Icons.location_on, size: 14, color: AppColors.textHint),
                    const SizedBox(width: 4),
                    Text(
                      user['branch'],
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.access_time, size: 14, color: AppColors.textHint),
                    const SizedBox(width: 4),
                    Text(
                      'Último acceso: ${user['lastLogin']}',
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showUserDialog({Map<String, dynamic>? user}) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(user == null ? 'Nuevo Usuario' : 'Editar Usuario'),
        content: SizedBox(
          width: 500,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'Nombre completo'),
                      controller: TextEditingController(text: user?['name']),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'Usuario'),
                      controller: TextEditingController(text: user?['username']),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'Email'),
                      controller: TextEditingController(text: user?['email']),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      decoration: const InputDecoration(labelText: 'Rol'),
                      value: user?['role'] ?? 'cashier',
                      items: const [
                        DropdownMenuItem(value: 'admin', child: Text('Administrador')),
                        DropdownMenuItem(value: 'cashier', child: Text('Cajero')),
                        DropdownMenuItem(value: 'delivery', child: Text('Repartidor')),
                        DropdownMenuItem(value: 'customer', child: Text('Cliente')),
                      ],
                      onChanged: (_) {},
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      decoration: const InputDecoration(labelText: 'Sucursal'),
                      value: 'suc1',
                      items: const [
                        DropdownMenuItem(value: 'suc1', child: Text('Sucursal Principal')),
                        DropdownMenuItem(value: 'suc2', child: Text('Sucursal Norte')),
                      ],
                      onChanged: (_) {},
                    ),
                  ),
                ],
              ),
              if (user == null) ...[
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        decoration: const InputDecoration(labelText: 'Contraseña'),
                        obscureText: true,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextField(
                        decoration: const InputDecoration(labelText: 'Confirmar contraseña'),
                        obscureText: true,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(user == null 
                      ? 'Usuario creado exitosamente' 
                      : 'Usuario actualizado'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
            child: Text(user == null ? 'Crear' : 'Guardar'),
          ),
        ],
      ),
    );
  }
}
