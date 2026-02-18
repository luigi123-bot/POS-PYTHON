import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pos_flutter/core/theme/app_theme.dart';

class SalesScreen extends ConsumerStatefulWidget {
  const SalesScreen({super.key});

  @override
  ConsumerState<SalesScreen> createState() => _SalesScreenState();
}

class _SalesScreenState extends ConsumerState<SalesScreen> {
  DateTime? _dateFrom;
  DateTime? _dateTo;
  String _statusFilter = 'all';

  // Demo sales
  final List<Map<String, dynamic>> _sales = [
    {
      'id': 1,
      'number': 'SUC001-20240218-001',
      'date': '18/02/2024 10:30',
      'customer': 'Cliente General',
      'total': 450.00,
      'status': 'completed',
      'payment': 'cash',
      'items': 5,
    },
    {
      'id': 2,
      'number': 'SUC001-20240218-002',
      'date': '18/02/2024 11:15',
      'customer': 'María García',
      'total': 320.50,
      'status': 'completed',
      'payment': 'card',
      'items': 3,
    },
    {
      'id': 3,
      'number': 'SUC001-20240218-003',
      'date': '18/02/2024 12:00',
      'customer': 'Juan Pérez',
      'total': 890.00,
      'status': 'pending',
      'payment': 'transfer',
      'items': 8,
    },
    {
      'id': 4,
      'number': 'SUC001-20240217-001',
      'date': '17/02/2024 15:30',
      'customer': 'Cliente General',
      'total': 125.00,
      'status': 'cancelled',
      'payment': 'cash',
      'items': 2,
    },
  ];

  double get _totalSales => _sales
      .where((s) => s['status'] == 'completed')
      .fold(0, (sum, s) => sum + s['total']);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ventas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.file_download),
            onPressed: () {},
            tooltip: 'Exportar',
          ),
          IconButton(
            icon: const Icon(Icons.print),
            onPressed: () {},
            tooltip: 'Imprimir',
          ),
        ],
      ),
      body: Column(
        children: [
          // Stats cards
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                _buildStatCard(
                  'Ventas Hoy',
                  '\$${_totalSales.toStringAsFixed(2)}',
                  Icons.attach_money,
                  AppColors.success,
                ),
                const SizedBox(width: 12),
                _buildStatCard(
                  'Transacciones',
                  '${_sales.length}',
                  Icons.receipt_long,
                  AppColors.primary,
                ),
                const SizedBox(width: 12),
                _buildStatCard(
                  'Promedio',
                  '\$${(_totalSales / _sales.where((s) => s['status'] == 'completed').length).toStringAsFixed(2)}',
                  Icons.trending_up,
                  AppColors.info,
                ),
                const SizedBox(width: 12),
                _buildStatCard(
                  'Pendientes',
                  '${_sales.where((s) => s['status'] == 'pending').length}',
                  Icons.pending_actions,
                  AppColors.warning,
                ),
              ],
            ),
          ),

          // Filters
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                // Date filter
                Expanded(
                  child: Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            final date = await showDatePicker(
                              context: context,
                              initialDate: DateTime.now(),
                              firstDate: DateTime(2020),
                              lastDate: DateTime.now(),
                            );
                            if (date != null) {
                              setState(() => _dateFrom = date);
                            }
                          },
                          icon: const Icon(Icons.calendar_today, size: 18),
                          label: Text(_dateFrom != null 
                              ? '${_dateFrom!.day}/${_dateFrom!.month}/${_dateFrom!.year}' 
                              : 'Desde'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            final date = await showDatePicker(
                              context: context,
                              initialDate: DateTime.now(),
                              firstDate: DateTime(2020),
                              lastDate: DateTime.now(),
                            );
                            if (date != null) {
                              setState(() => _dateTo = date);
                            }
                          },
                          icon: const Icon(Icons.calendar_today, size: 18),
                          label: Text(_dateTo != null 
                              ? '${_dateTo!.day}/${_dateTo!.month}/${_dateTo!.year}' 
                              : 'Hasta'),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                // Status filter
                DropdownButton<String>(
                  value: _statusFilter,
                  items: const [
                    DropdownMenuItem(value: 'all', child: Text('Todos los estados')),
                    DropdownMenuItem(value: 'completed', child: Text('Completadas')),
                    DropdownMenuItem(value: 'pending', child: Text('Pendientes')),
                    DropdownMenuItem(value: 'cancelled', child: Text('Canceladas')),
                  ],
                  onChanged: (value) {
                    setState(() => _statusFilter = value!);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Sales table
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
                        Expanded(flex: 2, child: Text('Folio', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 2, child: Text('Fecha', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 2, child: Text('Cliente', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Items', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Pago', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Total', style: TextStyle(fontWeight: FontWeight.w600))),
                        Expanded(flex: 1, child: Text('Estado', style: TextStyle(fontWeight: FontWeight.w600))),
                        SizedBox(width: 80, child: Text('Acciones', style: TextStyle(fontWeight: FontWeight.w600))),
                      ],
                    ),
                  ),

                  // Table body
                  Expanded(
                    child: ListView.separated(
                      itemCount: _sales.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (context, index) {
                        final sale = _sales[index];
                        return _buildSaleRow(sale);
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
                    fontSize: 18,
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

  Widget _buildSaleRow(Map<String, dynamic> sale) {
    Color statusColor;
    String statusText;
    
    switch (sale['status']) {
      case 'completed':
        statusColor = AppColors.success;
        statusText = 'Completada';
        break;
      case 'pending':
        statusColor = AppColors.warning;
        statusText = 'Pendiente';
        break;
      case 'cancelled':
        statusColor = AppColors.error;
        statusText = 'Cancelada';
        break;
      default:
        statusColor = AppColors.textSecondary;
        statusText = 'Desconocido';
    }

    IconData paymentIcon;
    switch (sale['payment']) {
      case 'cash':
        paymentIcon = Icons.money;
        break;
      case 'card':
        paymentIcon = Icons.credit_card;
        break;
      default:
        paymentIcon = Icons.swap_horiz;
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              sale['number'],
              style: const TextStyle(
                fontFamily: 'monospace',
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(sale['date']),
          ),
          Expanded(
            flex: 2,
            child: Text(sale['customer']),
          ),
          Expanded(
            flex: 1,
            child: Text('${sale['items']} items'),
          ),
          Expanded(
            flex: 1,
            child: Icon(paymentIcon, size: 20, color: AppColors.textSecondary),
          ),
          Expanded(
            flex: 1,
            child: Text(
              '\$${sale['total'].toStringAsFixed(2)}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                statusText,
                style: TextStyle(
                  fontSize: 12,
                  color: statusColor,
                  fontWeight: FontWeight.w600,
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
                  icon: const Icon(Icons.visibility, size: 18),
                  color: AppColors.primary,
                  onPressed: () => _showSaleDetails(sale),
                ),
                IconButton(
                  icon: const Icon(Icons.print, size: 18),
                  color: AppColors.textSecondary,
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showSaleDetails(Map<String, dynamic> sale) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Venta ${sale['number']}'),
        content: SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDetailRow('Fecha', sale['date']),
              _buildDetailRow('Cliente', sale['customer']),
              _buildDetailRow('Items', '${sale['items']}'),
              _buildDetailRow('Total', '\$${sale['total'].toStringAsFixed(2)}'),
              const Divider(height: 24),
              const Text(
                'Productos',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Column(
                  children: [
                    // Demo items
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Coca-Cola 600ml x2'),
                        Text('\$36.00'),
                      ],
                    ),
                    SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Sandwich Jamón x1'),
                        Text('\$45.00'),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cerrar'),
          ),
          if (sale['status'] == 'completed')
            ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.print, size: 18),
              label: const Text('Imprimir'),
            ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
