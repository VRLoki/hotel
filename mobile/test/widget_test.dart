import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_intel/main.dart';

void main() {
  testWidgets('App renders', (tester) async {
    await tester.pumpWidget(const HotelIntelApp());
    expect(find.byType(HotelIntelApp), findsOneWidget);
  });
}
