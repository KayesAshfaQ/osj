import 'package:flutter/material.dart';

abstract final class AppColors {
  static const teal = Color(0xFF00685F);
  static const darkTeal = Color(0xFF005049);
  static const background = Color(0xFFF8F9FF);
  static const ink = Color(0xFF0B1C30);
  static const muted = Color(0xFF3D4947);
  static const blue = Color(0xFFD3E4FE);
  static const border = Color(0xFFDCE5E4);
}

ThemeData juriesTheme() {
  final scheme = ColorScheme.fromSeed(seedColor: AppColors.teal).copyWith(
    primary: AppColors.teal,
    onPrimary: Colors.white,
    surface: Colors.white,
    onSurface: AppColors.ink,
    secondaryContainer: AppColors.blue,
    onSecondaryContainer: AppColors.ink,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: AppColors.background,
    fontFamily: 'Inter',
    fontFamilyFallback: const ['Noto Sans Bengali'],
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
        fontFamily: 'Source Serif 4',
        fontFamilyFallback: ['Noto Sans Bengali'],
        fontSize: 38,
        fontWeight: FontWeight.w600,
        height: 1.15,
        color: AppColors.ink,
      ),
      bodyLarge: TextStyle(fontSize: 16, height: 1.65, color: AppColors.ink),
      bodyMedium: TextStyle(fontSize: 14, height: 1.5, color: AppColors.muted),
    ),
    inputDecorationTheme: const InputDecorationTheme(
      border: InputBorder.none,
      hintStyle: TextStyle(color: AppColors.muted),
    ),
    dividerColor: AppColors.border,
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size(48, 48),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    ),
    dialogTheme: DialogThemeData(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
    ),
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: Colors.white,
      showDragHandle: true,
    ),
  );
}
