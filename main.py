import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill
from time import sleep

# Classe Turtle que contem todas as informações necessárias para uma tartaruga ser criada
class Turtle:
    amount = 0
    def __init__(self):
        self.name = f"turtle{Turtle.amount}"
        Turtle.amount += 1

# Classe Turtle_controller que contem todos os métodos necessários para controlar uma tartaruga. Essa classe é um nó do ROS para que possa se comunicar com o nó do TurtleSim
class Turtle_controller(Node):
    last_pose = Pose(x=float(0), y=float(0))
    def __init__(self):
        # Criando um nó no ROS com o nome "turtle_controller"
        super().__init__('turtle_controller')
        sleep(0.5)
        # Limpando a tela do TurtleSim
        self._kill_first_turtle()

    # Metodo para uso interno da classe para matar a primeira tartaruga criada
    def _kill_first_turtle(self):
        # Utilizando um método da classe herdada para utilizar o serviço kill do TurtleSim
        kill_client = self.create_client(Kill, 'kill')
        # Configurando a chamada do serviço
        kill_request = Kill.Request()
        kill_request.name = 'turtle1'
        # Chamando o serviço
        kill_client.call_async(kill_request)
        sleep(1)
    
    # Metodo para mover uma tartaruga
    def move_turtle(self, turtle:Turtle, x=None, y=None, z=None):
        # Utilizando um método da classe herdada para conseguir publicar no tópico cmd_vel do TurtleSim
        move_publisher = self.create_publisher(Twist, f'{turtle.name}/cmd_vel', 10)
        # Criando uma mensagem do tipo Twist (o que vai ser publicado)
        twist_msg = Twist()
        # Realizando verificações para modificar a mensagem que vai ser passada de acordo com os parâmetros requisitados
        if x:
            twist_msg.linear.x = x
        if y:
            twist_msg.linear.y = y
        if z:
            twist_msg.angular.z = z
        # Publicando a mensagem no tópico
        move_publisher.publish(twist_msg)
        sleep(1)
    
    # Metodo para criar um tartaruga
    def spawn_turtle(self, turtle:Turtle, x=None, y=None, theta=None):
        # Utilizando um método da classe herdada para utilizar o serviço spawn do TurtleSim
        spawn_client = self.create_client(Spawn, 'spawn')
        # Configurando a chamada do serviço
        spawn_request = Spawn.Request()
        # Realizando verificações para modificar a mensagem que vai ser passada de acordo com os parâmetros requisitados
        if x:
            spawn_request.x = x
        if y:
            spawn_request.y = y
        if theta:
            spawn_request.theta = theta
        spawn_request.name = turtle.name
        # Chamando o serviço
        spawn_client.call_async(spawn_request)
        sleep(1)

# Funcao para a tartaruga fazer a rota de 'ida'
def first_trajectory( turtle: Turtle , turtle_controller: Turtle_controller, turtmovements: list):
    # Faco um loop com um try que ele ficara retirando os valores do array ate nao conseguir mais. Quando der um erro (tentar dar pop em um array vazio), ele quebrara o while True.
    while True:
      try: 
         # Pelo fato de ser uma fila, estou retirando o primeiro item a entrar
         cords = turtmovements.pop(0)
         # Passo as coordenadas para o metodo move_turtle
         turtle_controller.move_turtle(turtle=turtle, x=float(cords[0]), y=float(cords[1]))
         sleep(1)
      except:
          break

#Funcao para a tartaruga fazer a rota de 'volta'
def go_home(turtle: Turtle , turtle_controller: Turtle_controller, turtmovements: list):
    # Faco um loop com um try que ele ficara retirando os valores do array ate nao conseguir mais. Quando der um erro (tentar dar pop em um array vazio), ele quebrara o while True.
    while True:
      try: 
         # Pelo fato de ser uma pilha, estou retirando o ultimo item a entrar
         cords = turtmovements.pop()
         # Como desejo que a tartaruga faca exatamente o caminho oposto, multiplico as coordenadas por -1
         turtle_controller.move_turtle(turtle=turtle, x=float(-1*cords[0]), y=float(-1*cords[1]))
         sleep(1)
      except:
          break
    

# Função principal de execução
def main(args=None):
    # Inicializando o ROS
    rclpy.init(args=args)

    # Instanciando um objeto Turtle_controller
    turtle_controller = Turtle_controller()

    # Instanciando um objeto tartaruga (aquela que ira se movimentar)
    turtle = Turtle()

    # Criando um array que contem como a tartaruga deve se mover a cada ponto. Esse array sera utilizado como fila para a ida e pilha para a volta
    points = []

    # Alimentando minha estrutura de dados armazendo uma tupla(x,y) ao final do array
    points.append((0.0, 0.5))
    points.append((0.5, 0.0))
    points.append((0.0, 0.5))
    points.append((0.5, 0.0))
    points.append((0.0, 1.0))
    points.append((1.0, 0.0))

    # Criando uma copia do array de pontos pois como vou utilizar o metodo pop, a variavel que for passada para a funcao sera alterada, ou seja, se eu passar o array original, ele ao final estara vazio.
    points_to_go = points.copy()

    # Criando uma copia do array de pontos pois como vou utilizar o metodo pop, a variavel que for passada para a funcao sera alterada, ou seja, se eu passar o array original, ele ao final estara vazio.
    points_to_go_back = points.copy()

    # Criando a tartaruga na tela
    turtle_controller.spawn_turtle(turtle=turtle, x=1.0, y=2.0)
    sleep(0.3)

    # Executando a funcao para a tartaruga fazer a rota de 'ida'
    first_trajectory(turtle=turtle, turtle_controller=turtle_controller, turtmovements=points_to_go)

    # Executando a funcao para a tartaruga fazer a rota de 'volta'
    go_home(turtle=turtle, turtle_controller=turtle_controller, turtmovements=points_to_go_back)

    # Apagando o no, assumindo que todas as tarefas ja foram executadas com sucessso
    turtle_controller.destroy_node()
    
    # Finalizando o rclpy
    rclpy.shutdown()

# Ponto de inicialização do programa
if __name__ == '__main__':
    main()
