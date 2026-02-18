import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pos_flutter/core/theme/app_theme.dart';

class ProductsScreen extends ConsumerStatefulWidget {
  const ProductsScreen({super.key});

  @override
  ConsumerState<ProductsScreen> createState() => _ProductsScreenState();
}

class _ProductsScreenState extends ConsumerState<ProductsScreen> {
  final _searchController = TextEditingController();
  String _selectedCategory = 'all';

  // Demo products
  final List<Map<String, dynamic>> _products = [
    {'id': 1, 'sku': 'BEB001', 'name': 'Coca-Cola 600ml', 'price': 18.00, 'cost': 12.00, 'stock': 50, 'category': 'Bebidas', 'active': true},
    {'id': 2, 'sku': 'BEB002', 'name': 'Agua Natural 1L', 'price': 12.00, 'cost': 6.00, 'stock': 100, 'category': 'Bebidas', 'active': true},
    {'id': 3, 'sku': 'BEB003', 'name': 'Jugo de Naranja 500ml', 'price': 25.00, 'cost': 15.00, 'stock': 30, 'category': 'Bebidas', 'active': true},
    {'id': 4, 'sku': 'ALI001', 'name': 'Sandwich Jamón y Queso', 'price': 45.00, 'cost': 25.00, 'stock': 20, 'category': 'Alimentos', 'active': true},
    {'id': 5, 'sku': 'ALI002', 'name': 'Ensalada César', 'price': 55.00, 'cost': 30.00, 'stock': 5, 'category': 'Alimentos', 'active': true},
    {'id': 6, 'sku': 'SNK001', 'name': 'Papas Fritas 150g', 'price': 22.00, 'cost': 12.00, 'stock': 40, 'category': 'Snacks', 'active': true},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Productos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.file_download),
            onPressed: () {},
            tooltip: 'Exportar',
          ),
          const SizedBox(width: 8),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showProductDialog,
        icon: const Icon(Icons.add),
        label: const Text('Nuevo Producto'),
      ),
      body: Column(
        children: [
          // Search and filters
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      hintText: 'Buscar productos...',
                      prefixIcon: Icon(Icons.search),
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                ),
                const SizedBox(width: 16),
                DropdownButton<String>(
                  value: _selectedCategory,
                  items: const [
                    DropdownMenuItem(value: 'all', child: Text('Todas las categorías')),
                    DropdownMenuItem(value: 'bebidas', child: Text('Bebidas')),
                    DropdownMenuItem(value: 'alimentos', child: Text('Alimentos')),
                    DropdownMenuItem(value: 'snacks', child: Text('Snacks')),
                  ],
                  onChanged: (value) {
                    setState(() => _selectedCategory = value!);
                  },
                ),
              ],
            ),
          ),

          // Stats cards
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _buildStatCard('Total Productos', '${_products.length}', Icons.inventory_2, AppColors.primary),
                const SizedBox(width: 12),
                _buildStatCard('Stock Bajo', '2', Icons.warning, AppColors.warning),
                const SizedBox(width: 12),
                _buildStatCard('Sin Stock', '0', Icons.error, AppColors.error),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Products table
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                children: [
                  // Table header
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceVariant,
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                    ),
                    child: const Row(
                      children: [
                        Expanded(flex: 1, child: Text('SKU', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 3, child: Text('Producto', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Categoría', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Precio', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Stock', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Estado', style: TextStyle(fontWeight: FontWeight.w600))),
                        SizedBox(width: 80, child: Text('Acciones', style: TextStyle(fontWeight: FontWeight.w600))),
                      ],
                    ),
                  ),

                  // Table body
                  Expanded(
                    child: ListView.separated(
                      itemCount: _products.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (context, index) {
                        final product = _products[index];
                        return _buildProductRow(product);
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductRow(Map<String, dynamic> product) {
    final isLowStock = product['stock'] <= 10;
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            flex: 1,
            child: Text(
              product['sku'],
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ),
          Expanded(
            flex: 3,
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.inventory_2, color: AppColors.textHint),
                ),
                const SizedBox(width: 12),
                Text(product['name'], style: const TextStyle(fontWeight: FontWeight.w500)),
              ],
            ),
          ),
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                product['category'],
                style: const TextStyle(fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              '\$${product['price'].toStringAsFixed(2)}',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            flex: 1,
            child: Row(
              children: [
                if (isLowStock)
                  const Icon(Icons.warning, color: AppColors.warning, size: 16),
                const SizedBox(width: 4),
                Text(
                  '${product['stock']}',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    color: isLowStock ? AppColors.warning : AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: product['active'] 
                    ? AppColors.success.withOpacity(0.1)
                    : AppColors.error.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                product['active'] ? 'Activo' : 'Inactivo',
                style: TextStyle(
                  fontSize: 12,
                  color: product['active'] ? AppColors.success : AppColors.error,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
          SizedBox(
            width: 80,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, size: 18),
                  color: AppColors.primary,
                  onPressed: () => _showProductDialog(product: product),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, size: 18),
                  color: AppColors.error,
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showProductDialog({Map<String, dynamic>? product}) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(product == null ? 'Nuevo Producto' : 'Editar Producto'),
        content: SizedBox(
          width: 500,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'SKU'),
                      controller: TextEditingController(text: product?['sku']),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'Código de barras'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextField(
                decoration: const InputDecoration(labelText: 'Nombre del producto'),
                controller: TextEditingController(text: product?['name']),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'Precio', prefixText: '\$ '),
                      controller: TextEditingController(text: product?['price']?.toString()),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(labelText: 'Costo', prefixText: '\$ '),
                      controller: TextEditingController(text: product?['cost']?.toString()),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(labelText: 'Categoría'),
                value: product?['category']?.toLowerCase(),
                items: const [
                  DropdownMenuItem(value: 'bebidas', child: Text('Bebidas')),
                  DropdownMenuItem(value: 'alimentos', child: Text('Alimentos')),
                  DropdownMenuItem(value: 'snacks', child: Text('Snacks')),
                ],
                onChanged: (_) {},
              ),
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
                  content: Text(product == null 
                      ? 'Producto creado exitosamente' 
                      : 'Producto actualizado'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
            child: Text(product == null ? 'Crear' : 'Guardar'),
          ),
        ],
      ),
    );
  }
}
