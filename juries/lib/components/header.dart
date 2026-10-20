import 'package:jaspr/dom.dart';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr_lucide/jaspr_lucide.dart';
import '../i18n/locale_provider.dart';
import 'app_link.dart';

class Navbar extends StatefulComponent {
  const Navbar({super.key});

  @override
  State<Navbar> createState() => _NavbarState();
}

class _NavbarState extends State<Navbar> {
  bool isMenuOpen = false;

  void toggleMenu() {
    setState(() {
      isMenuOpen = !isMenuOpen;
    });
  }

  @override
  Component build(BuildContext context) {
    final i18n = LocaleProvider.of(context);
    final isEn = i18n.locale == 'en';

    return header(
      classes:
          'fixed top-0 left-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-juris-main/10 transition-all duration-300',
      [
        div(classes: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center', [
          // Logo
          a(href: '/', classes: 'flex items-center gap-2 text-juris-main', [
            Gavel(classes: 'w-6 h-6 fill-current'),
            span(classes: 'font-serif text-2xl font-bold tracking-tight', [Component.text('OSJ')]),
          ]),

          // Navigation Links
          nav(classes: 'hidden lg:flex items-center gap-6', [
            for (var item in [
              (i18n.getString('nav_home'), '/'),
              (i18n.getString('nav_how_it_works'), '#how-it-works'),
              (i18n.getString('nav_mission'), '#mission'),
            ])
              a(href: item.$2, classes: 'text-sm font-medium text-juris-text hover:text-juris-main transition-colors', [
                Component.text(item.$1),
              ]),
          ]),

          // Action Buttons
          div(classes: 'flex items-center gap-4', [
            div(classes: 'flex items-center bg-gray-100 rounded-full p-1', [
              button(
                classes: isEn
                    ? 'px-3 py-1 text-xs font-medium rounded-full bg-white shadow-sm text-juris-main cursor-pointer'
                    : 'px-3 py-1 text-xs font-medium rounded-full text-gray-500 hover:text-gray-900 transition-colors cursor-pointer',
                onClick: () => i18n.onLocaleChange('en'),
                [Component.text('EN')],
              ),
              button(
                classes: !isEn
                    ? 'px-3 py-1 text-xs font-medium rounded-full bg-white shadow-sm text-juris-main cursor-pointer'
                    : 'px-3 py-1 text-xs font-medium rounded-full text-gray-500 hover:text-gray-900 transition-colors cursor-pointer',
                onClick: () => i18n.onLocaleChange('bn'),
                [Component.text('BN')],
              ),
            ]),

            const AppLink(
              classes:
                  'hidden lg:block bg-juris-main text-white font-medium text-sm px-5 py-2.5 rounded-lg hover:bg-juris-dark transition-all shadow-sm active:scale-95',
            ),

            // Mobile menu toggle
            button(
              classes:
                  'lg:hidden p-2 -mr-2 text-juris-main hover:bg-gray-100 rounded-lg transition-colors cursor-pointer',
              onClick: toggleMenu,
              [
                isMenuOpen ? X(classes: 'w-6 h-6') : Menu(classes: 'w-6 h-6'),
              ],
            ),
          ]),
        ]),

        // Mobile Menu Dropdown
        div(
          classes: isMenuOpen
              ? 'lg:hidden overflow-hidden transition-all duration-300 ease-in-out bg-white/95 backdrop-blur-md max-h-[500px] border-t border-juris-main/10 opacity-100'
              : 'lg:hidden overflow-hidden transition-all duration-300 ease-in-out bg-white/95 backdrop-blur-md max-h-0 opacity-0',
          [
            div(classes: 'max-w-7xl mx-auto px-4 sm:px-6 py-6 flex flex-col gap-4', [
              for (var item in [
                (i18n.getString('nav_home'), '/'),
                (i18n.getString('nav_how_it_works'), '#how-it-works'),
                (i18n.getString('nav_mission'), '#mission'),
              ])
                a(
                  href: item.$2,
                  classes: 'text-base font-medium text-juris-text hover:text-juris-main transition-colors',
                  [
                    Component.text(item.$1),
                  ],
                ),

              hr(classes: 'border-juris-main/10 my-2'),

              div(classes: 'flex flex-col gap-3', [
                const AppLink(
                  classes:
                      'text-center w-full bg-juris-main text-white font-medium text-base px-5 py-2.5 rounded-lg hover:bg-juris-dark transition-colors shadow-sm',
                ),
              ]),
            ]),
          ],
        ),
      ],
    );
  }
}
