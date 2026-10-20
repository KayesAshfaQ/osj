import 'dart:convert';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:universal_web/web.dart' as web;
import 'package:http/http.dart' as http;
import 'toast.dart';
import '../i18n/locale_provider.dart';
import '../config/origin_config.dart';

class WaitlistForm extends StatefulComponent {
  const WaitlistForm({super.key});

  @override
  State<WaitlistForm> createState() => _WaitlistFormState();
}

class _WaitlistFormState extends State<WaitlistForm> {
  String email = '';
  bool isLoading = false;
  String? toastMessage;
  ToastType toastType = ToastType.success;

  void handleSubmit(web.Event event) async {
    event.preventDefault();
    if (email.isEmpty || !email.contains('@')) {
      setState(() {
        toastMessage = 'Please enter a valid email address.';
        toastType = ToastType.error;
      });
      return;
    }

    setState(() {
      isLoading = true;
      toastMessage = null;
    });

    try {
      final base = Uri.parse(OriginConfig.apiOrigin);
      final response = await http
          .post(
            base.resolve('/api/waitlist'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'email': email}),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 201) {
        setState(() {
          toastMessage = 'Demo submission accepted. No subscription is created.';
          toastType = ToastType.success;
          email = '';
        });
      } else if (response.statusCode == 409) {
        setState(() {
          toastMessage = 'Unable to submit. Please check your email and try again.';
          toastType = ToastType.error;
        });
      } else {
        setState(() {
          toastMessage = 'An error occurred. Please try again later.';
          toastType = ToastType.error;
        });
      }
    } catch (e) {
      setState(() {
        toastMessage = 'Network error. Please check your connection and try again.';
        toastType = ToastType.error;
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void closeToast() {
    setState(() {
      toastMessage = null;
    });
  }

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    return div(classes: 'w-full max-w-md mx-auto', [
      // Form pill container — matches target HTML exactly
      form(
        classes:
            'max-w-md mx-auto bg-white p-2 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-200/50 flex flex-col sm:flex-row gap-2',
        id: 'waitlist',
        events: {'submit': handleSubmit},
        [
          // Email input
          input(
            type: InputType.email,
            classes:
                'flex-1 min-w-96 px-4 py-3 text-base text-juris-text bg-transparent border-0 focus:ring-0 placeholder:text-juris-gray/50 rounded-xl outline-none',
            attributes: {
              'placeholder': i18n.getString('hero_waitlist_form_placeholder'),
              'required': 'true',
              'autocomplete': 'email',
            },
            value: email,
            events: events(onInput: (String value) => setState(() => email = value)),
          ),
          // Submit button
          button(
            type: ButtonType.submit,
            disabled: isLoading,
            classes:
                'inline-flex items-center justify-center gap-2 px-4 py-3 border border-transparent text-base font-semibold rounded-xl text-white bg-juris-main hover:bg-juris-dark shadow-sm transition-colors sm:w-auto w-full disabled:opacity-60 disabled:cursor-not-allowed whitespace-nowrap',
            [
              if (isLoading) ...[
                span(
                  classes: 'w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin',
                  [],
                ),
                Component.text(i18n.getString('hero_waitlist_btn_loading')),
              ] else
                Component.text(i18n.getString('hero_waitlist_btn_text')),
            ],
          ),
        ],
      ),

      // Toast feedback
      if (toastMessage != null)
        Toast(
          message: toastMessage!,
          type: toastType,
          onClose: closeToast,
        ),
    ]);
  }
}
