import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/estacion.dart';

void main() => runApp(const SMATApp());
class SMATApp extends StatelessWidget {
  const SMATApp({super.key});
  @override
  Widget build(BuildContext context) {
  return MaterialApp(home: const HomePage(), debugShowCheckedModeBanner: false);
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;
  
  @override
  void initState() {
    super.initState();
    futureEstaciones = ApiService().fetchEstaciones();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
    appBar: AppBar(title: const Text('SMAT - Monitoreo Móvil')),
    body: FutureBuilder<List<Estacion>>(
      future: futureEstaciones,
      builder: (context, snapshot) {
      if (snapshot.connectionState == ConnectionState.waiting) {
      return const Center(child: CircularProgressIndicator());
      } else if (snapshot.hasError) {
      return Center(child: Text('❌ Error de conexión'));
      } else {
        return ListView.builder(
          itemCount: snapshot.data!.length,
          itemBuilder: (context, index) {
            final est = snapshot.data![index];
            return ListTile(
              leading: const Icon(Icons.satellite_alt),
              title: Text(est.nombre),
              subtitle: Text(est.ubicacion),
              );
            },
          );
        }
       },
      ),
    );
  }
}