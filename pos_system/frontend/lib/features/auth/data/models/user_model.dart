class UserModel {
  final int id;
  final String email;
  final String username;
  final String fullName;
  final String? phone;
  final bool isActive;
  final bool isSuperuser;
  final int roleId;
  final int? primaryBranchId;
  final DateTime createdAt;
  final DateTime? lastLogin;
  final RoleModel? role;
  final BranchModel? primaryBranch;
  final List<String> permissions;

  UserModel({
    required this.id,
    required this.email,
    required this.username,
    required this.fullName,
    this.phone,
    required this.isActive,
    required this.isSuperuser,
    required this.roleId,
    this.primaryBranchId,
    required this.createdAt,
    this.lastLogin,
    this.role,
    this.primaryBranch,
    this.permissions = const [],
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      username: json['username'],
      fullName: json['full_name'],
      phone: json['phone'],
      isActive: json['is_active'] ?? true,
      isSuperuser: json['is_superuser'] ?? false,
      roleId: json['role_id'],
      primaryBranchId: json['primary_branch_id'],
      createdAt: DateTime.parse(json['created_at']),
      lastLogin: json['last_login'] != null 
          ? DateTime.parse(json['last_login']) 
          : null,
      role: json['role'] != null ? RoleModel.fromJson(json['role']) : null,
      primaryBranch: json['primary_branch'] != null 
          ? BranchModel.fromJson(json['primary_branch']) 
          : null,
      permissions: json['permissions'] != null 
          ? List<String>.from(json['permissions']) 
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'full_name': fullName,
      'phone': phone,
      'is_active': isActive,
      'is_superuser': isSuperuser,
      'role_id': roleId,
      'primary_branch_id': primaryBranchId,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
      'permissions': permissions,
    };
  }
  
  bool hasPermission(String permission) => permissions.contains(permission);
  
  bool hasAnyPermission(List<String> perms) => 
      perms.any((p) => permissions.contains(p));
}

class RoleModel {
  final int id;
  final String name;
  final String displayName;
  final String? description;
  final bool isSystem;

  RoleModel({
    required this.id,
    required this.name,
    required this.displayName,
    this.description,
    required this.isSystem,
  });

  factory RoleModel.fromJson(Map<String, dynamic> json) {
    return RoleModel(
      id: json['id'],
      name: json['name'],
      displayName: json['display_name'],
      description: json['description'],
      isSystem: json['is_system'] ?? false,
    );
  }
}

class BranchModel {
  final int id;
  final String code;
  final String name;
  final String? address;
  final String? city;
  final String? phone;
  final bool isActive;
  final bool isMain;

  BranchModel({
    required this.id,
    required this.code,
    required this.name,
    this.address,
    this.city,
    this.phone,
    required this.isActive,
    required this.isMain,
  });

  factory BranchModel.fromJson(Map<String, dynamic> json) {
    return BranchModel(
      id: json['id'],
      code: json['code'],
      name: json['name'],
      address: json['address'],
      city: json['city'],
      phone: json['phone'],
      isActive: json['is_active'] ?? true,
      isMain: json['is_main'] ?? false,
    );
  }
}
