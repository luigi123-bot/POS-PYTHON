class ApiConstants {
  // Base URL - Change this for production
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = '/api/v1';
  
  // Auth endpoints
  static const String login = '$apiVersion/auth/login';
  static const String me = '$apiVersion/auth/me';
  static const String refresh = '$apiVersion/auth/refresh';
  
  // Users endpoints
  static const String users = '$apiVersion/users';
  
  // Roles endpoints
  static const String roles = '$apiVersion/roles';
  static const String permissions = '$apiVersion/roles/permissions';
  
  // Branches endpoints
  static const String branches = '$apiVersion/branches';
  
  // Products endpoints
  static const String products = '$apiVersion/products';
  static const String categories = '$apiVersion/products/categories';
  
  // Sales endpoints
  static const String sales = '$apiVersion/sales';
  static const String deliveries = '$apiVersion/sales/delivery/pending';
  static const String salesReports = '$apiVersion/sales/reports/summary';
  
  // Timeouts
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
}

class StorageKeys {
  static const String accessToken = 'access_token';
  static const String userId = 'user_id';
  static const String userRole = 'user_role';
  static const String branchId = 'branch_id';
  static const String userData = 'user_data';
}
