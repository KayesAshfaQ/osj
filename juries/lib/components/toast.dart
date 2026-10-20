import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:jaspr_lucide/jaspr_lucide.dart' hide Key;

enum ToastType { success, error, info, warning }

class Toast extends StatelessComponent {
  final String message;
  final ToastType type;
  final VoidCallback onClose;

  const Toast({
    super.key,
    required this.message,
    this.type = ToastType.success,
    required this.onClose,
  });

  // Convenience constructor for backward compatibility
  factory Toast.fromError({
    Key? key,
    required String message,
    required bool isError,
    required VoidCallback onClose,
  }) {
    return Toast(
      key: key,
      message: message,
      type: isError ? ToastType.error : ToastType.success,
      onClose: onClose,
    );
  }

  String get _bgColor => switch (type) {
    ToastType.success => 'bg-green-50',
    ToastType.error => 'bg-red-50',
    ToastType.info => 'bg-blue-50',
    ToastType.warning => 'bg-amber-50',
  };

  String get _borderColor => switch (type) {
    ToastType.success => 'border-green-200',
    ToastType.error => 'border-red-200',
    ToastType.info => 'border-blue-200',
    ToastType.warning => 'border-amber-200',
  };

  String get _iconBg => switch (type) {
    ToastType.success => 'bg-green-500',
    ToastType.error => 'bg-red-500',
    ToastType.info => 'bg-blue-500',
    ToastType.warning => 'bg-amber-400',
  };

  String get _textColor => switch (type) {
    ToastType.success => 'text-green-800',
    ToastType.error => 'text-red-800',
    ToastType.info => 'text-blue-800',
    ToastType.warning => 'text-amber-800',
  };

  String get _closeHover => switch (type) {
    ToastType.success => 'hover:bg-green-100',
    ToastType.error => 'hover:bg-red-100',
    ToastType.info => 'hover:bg-blue-100',
    ToastType.warning => 'hover:bg-amber-100',
  };

  Component get _icon => switch (type) {
    ToastType.success => Check(classes: 'w-3 h-3 text-white'),
    ToastType.error => X(classes: 'w-3 h-3 text-white'),
    ToastType.info => Info(classes: 'w-3 h-3 text-white'),
    ToastType.warning => TriangleAlert(classes: 'w-3 h-3 text-white'),
  };

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'mt-3 flex items-start gap-3 px-4 py-3 rounded-xl border $_bgColor $_borderColor shadow-sm',
      [
        // Icon circle
        div(
          classes: 'flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full mt-0.5 $_iconBg',
          [_icon],
        ),
        // Message
        div(
          classes: 'flex-1 text-sm font-medium leading-snug $_textColor',
          [Component.text(message)],
        ),
        // Close button
        button(
          type: ButtonType.button,
          onClick: onClose,
          classes:
              'flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-lg text-current opacity-60 hover:opacity-100 transition-opacity $_closeHover cursor-pointer',
          [X(classes: 'w-3.5 h-3.5')],
        ),
      ],
    );
  }
}
