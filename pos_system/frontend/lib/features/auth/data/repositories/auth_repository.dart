import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pos_flutter/core/constants/api_constants.dart';
import 'package:pos_flutter/core/network/dio_client.dart';
import 'package:pos_flutter/features/auth/data/models/user_model.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.read(dioProvider));
});

class AuthRepository {
  final Dio _dio;
  
  AuthRepository(this._dio);
  
  Future<AuthResponse> login(String username, String password) async {
    try {
      final response = await _dio.post(
        ApiConstants.login,
        data: {
          'username': username,
          'password': password,
        },
      );
      
      return AuthResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        e.response?.data['detail'] ?? 'Error de autenticación',
        e.response?.statusCode,
      );
    }
  }
  
  Future<UserModel> getCurrentUser() async {
    try {
      final response = await _dio.get(ApiConstants.me);
      return UserModel.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(
        e.response?.data['detail'] ?? 'Error al obtener usuario',
        e.response?.statusCode,
      );
    }
  }
  
  Future<String> refreshToken() async {
    try {
      final response = await _dio.post(ApiConstants.refresh);
      return response.data['access_token'];
    } on DioException catch (e) {
      throw ApiException(
        'Error al refrescar token',
        e.response?.statusCode,
      );
    }
  }
}

class AuthResponse {
  final String accessToken;
  final String tokenType;
  final UserModel user;
  
  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });
  
  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'],
      tokenType: json['token_type'],
      user: UserModel.fromJson(json['user']),
    );
  }
}
