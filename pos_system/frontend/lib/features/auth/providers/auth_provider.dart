import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:pos_flutter/core/constants/api_constants.dart';
import 'package:pos_flutter/core/network/dio_client.dart';
import 'package:pos_flutter/features/auth/data/models/user_model.dart';
import 'package:pos_flutter/features/auth/data/repositories/auth_repository.dart';

// Auth State
class AuthState {
  final UserModel? user;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;
  
  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
    this.isAuthenticated = false,
  });
  
  AuthState copyWith({
    UserModel? user,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
    );
  }
}

// Auth Notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;
  final FlutterSecureStorage _storage;
  
  AuthNotifier(this._authRepository, this._storage) : super(const AuthState());
  
  Future<void> checkAuthStatus() async {
    state = state.copyWith(isLoading: true);
    
    try {
      final token = await _storage.read(key: StorageKeys.accessToken);
      
      if (token != null) {
        final user = await _authRepository.getCurrentUser();
        state = AuthState(
          user: user,
          isAuthenticated: true,
          isLoading: false,
        );
      } else {
        state = const AuthState(isLoading: false);
      }
    } catch (e) {
      await _storage.deleteAll();
      state = AuthState(isLoading: false, error: e.toString());
    }
  }
  
  Future<bool> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _authRepository.login(username, password);
      
      // Save token and user data
      await _storage.write(
        key: StorageKeys.accessToken,
        value: response.accessToken,
      );
      await _storage.write(
        key: StorageKeys.userData,
        value: jsonEncode(response.user.toJson()),
      );
      await _storage.write(
        key: StorageKeys.userRole,
        value: response.user.role?.name ?? 'customer',
      );
      
      state = AuthState(
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      );
      
      return true;
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, error: e.message);
      return false;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Error de conexión');
      return false;
    }
  }
  
  Future<void> logout() async {
    await _storage.deleteAll();
    state = const AuthState();
  }
  
  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Provider
final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.read(authRepositoryProvider);
  final storage = ref.read(secureStorageProvider);
  return AuthNotifier(authRepository, storage);
});
